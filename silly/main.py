import logging
import starlette.applications
import sillyorm
import signal
import functools
import multiprocessing
import time
import os
import re
import pathlib
import hypercorn
import hypercorn.asyncio
import asyncio
from . import modload, mod, http, globalvars

_logger = logging.getLogger(__name__)


class CustomRegistry(sillyorm.Registry):
    @staticmethod
    def _table_cmp_should_include(obj, name, type_, reflected, compare_to) -> bool:
        return not (type_ == "table" and re.match(r"__silly_alembic_version_.+", name) is not None)


_routes = None


def init(config, modules_to_install=[], modules_to_uninstall=[], update=False):
    global _routes
    config.apply_cfg()
    _logger.info("silly version [...] starting")
    modload.add_module_paths([str(pathlib.Path(__file__).parent / "modules")])
    globalvars.registry = CustomRegistry(config["connstr"])
    mod.load_core(update and not modules_to_uninstall)
    if update:
        if modules_to_install and modules_to_uninstall:
            raise Exception("can't install and uninstall stuff at the same time")
        if not modules_to_install and not modules_to_uninstall:
            mod.update([], False)
        elif modules_to_install:
            mod.update(modules_to_install, False)
        elif modules_to_uninstall:
            mod.load_all()
            mod.update(modules_to_uninstall, True)
    else:
        mod.load_all()
    _routes = http.init_routers()


def _worker(worker_type, shutdown_event, main_process_queue, **kwargs):
    if main_process_queue is not None:
        globalvars.threadlocal.main_process_queue = main_process_queue
    match worker_type:
        case "web":
            app = kwargs["starlette_app"]
            config = kwargs["hypercorn_config"]
            sockets = kwargs["hypercorn_sockets"]
            # .. the hypercorn.asyncio.serve function does not pass through the sockets
            # argument, so we need to do the things it does ourselves
            shutdown_trigger = None
            if shutdown_event is not None:
                shutdown_trigger = functools.partial(
                    hypercorn.utils.check_multiprocess_shutdown_event,
                    shutdown_event,
                    asyncio.sleep,
                )
            asyncio.run(
                hypercorn.asyncio.worker_serve(
                    hypercorn.utils.wrap_app(app, config.wsgi_max_body_size, None),
                    config,
                    shutdown_trigger=shutdown_trigger,
                    sockets=sockets,
                )
            )


def run(config):
    starlette_app = starlette.applications.Starlette(
        debug=True,  # FIXME: careful!
        routes=_routes,
    )
    hypercorn_config = hypercorn.Config()
    hypercorn_config.bind = "0.0.0.0:5000"
    hypercorn_config.accesslog = "-"
    hypercorn_config.errorlog = "-"
    hypercorn_config.use_reuse_port = True
    # we want the sockets shared between the workers
    hypercorn_sockets = hypercorn_config.create_sockets()

    def _close_hypercorn_sockets():
        for sl in [
            hypercorn_sockets.secure_sockets,
            hypercorn_sockets.insecure_sockets,
            hypercorn_sockets.quic_sockets,
        ]:
            for socket in sl:
                socket.close()

    # only fork will work for us at the moment
    multiprocessing.set_start_method("fork")

    shutdown_event = multiprocessing.Event()
    main_process_queue = multiprocessing.Queue()

    running = True

    def stop_workers(*args):
        nonlocal running
        running = False
        shutdown_event.set()

    # prior to forking, we ignore SIGINT so the child processes will also ignore it
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    processes = []
    for _ in range(3):
        p = multiprocessing.Process(
            target=_worker,
            args=("web", shutdown_event, main_process_queue),
            kwargs={
                "starlette_app": starlette_app,
                "hypercorn_config": hypercorn_config,
                "hypercorn_sockets": hypercorn_sockets,
            },
        )
        p.start()
        processes.append(p)

    # now we handle SIGINT (and more) again
    for signal_name in ["SIGINT", "SIGTERM"]:
        signal.signal(getattr(signal, signal_name), stop_workers)

    def join_all():
        for p in processes:
            p.join()

        # close all the hypercorn sockets, otherwise when we reexec they'll still be open and we get an address in use error...
        _close_hypercorn_sockets()

    while running:
        if not main_process_queue.empty():
            task = main_process_queue.get()
            if isinstance(task, list) and len(task) >= 1 and task[0] == "mod.update":
                stop_workers()
                join_all()
                mod.update(*task[1:])
                break
        time.sleep(1)

    join_all()
