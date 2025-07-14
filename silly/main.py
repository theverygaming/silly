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
    _logger.info("worker of type '%s' with PID %s starting", worker_type, os.getpid())
    if main_process_queue is not None:
        globalvars.threadlocal.main_process_queue = main_process_queue
    match worker_type:
        case "web":
            app = kwargs["starlette_app"]
            config = kwargs["hypercorn_config"]
            sockets = kwargs["hypercorn_sockets"]
            # .. the hypercorn.asyncio.serve function does not pass through the sockets
            # argument, so we need to do the things it does ourselves
            asyncio.run(
                hypercorn.asyncio.worker_serve(
                    hypercorn.utils.wrap_app(app, config.wsgi_max_body_size, None),
                    config,
                    shutdown_trigger=functools.partial(
                        hypercorn.utils.check_multiprocess_shutdown_event,
                        shutdown_event,
                        asyncio.sleep,
                    ),
                    sockets=sockets,
                )
            )


def _web_init():
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
    return (starlette_app, hypercorn_config, hypercorn_sockets)


def _close_hypercorn_sockets(hypercorn_sockets):
    for sl in [
        hypercorn_sockets.secure_sockets,
        hypercorn_sockets.insecure_sockets,
        hypercorn_sockets.quic_sockets,
    ]:
        for socket in sl:
            socket.close()


def _mp_spawn_worker(config, worker_type, shutdown_event, main_process_queue):
    init(config)
    w_kwargs = {}
    if worker_type == "web":
        w_kwargs["starlette_app"], w_kwargs["hypercorn_config"], w_kwargs["hypercorn_sockets"] = (
            _web_init()
        )
    _worker(
        worker_type,
        shutdown_event,
        main_process_queue,
        **w_kwargs,
    )


def run(config):
    # Windows doesn't support shit
    use_fork = os.name != "nt" and False

    if use_fork:
        multiprocessing.set_start_method("fork")
    else:
        multiprocessing.set_start_method("spawn")

    shutdown_event = multiprocessing.Event()
    main_process_queue = multiprocessing.Queue()

    running = True

    def stop_workers(*args):
        nonlocal running
        running = False
        shutdown_event.set()

    if use_fork:
        starlette_app, hypercorn_config, hypercorn_sockets = _web_init()

    # without fork, only one web worker is supported
    if not use_fork and config["workers-web"] > 1:
        raise Exception("without fork, only a single web worker is supported")

    # prior to forking, we ignore SIGINT so the child processes will also ignore it
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    processes = []
    for wktype in ["web"] * config["workers-web"] + ["cron"] * config["workers-cron"]:
        if use_fork:
            p = multiprocessing.Process(
                target=_worker,
                args=(wktype, shutdown_event, main_process_queue),
                kwargs={
                    "starlette_app": starlette_app,
                    "hypercorn_config": hypercorn_config,
                    "hypercorn_sockets": hypercorn_sockets,
                },
            )
        else:
            p = multiprocessing.Process(
                target=_mp_spawn_worker,
                args=(config, wktype, shutdown_event, main_process_queue),
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
        if use_fork:
            _close_hypercorn_sockets(hypercorn_sockets)

    while running:
        if not main_process_queue.empty():
            task = main_process_queue.get()
            if isinstance(task, list) and len(task) >= 1 and task[0] == "mod.update":
                stop_workers()
                join_all()
                mod.update(*task[1:])
                break
        time.sleep(0.25)

    join_all()
