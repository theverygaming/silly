import logging
import flask
import sillyorm
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


def init(connstr, modules_to_install=[], modules_to_uninstall=[], update=False):
    if modules_to_install and modules_to_uninstall:
        raise Exception("can't install and uninstall stuff at the same time")
    _logger.info("silly version [...] starting")
    modload.add_module_paths([str(pathlib.Path(__file__).parent / "modules")])
    globalvars.registry = CustomRegistry(connstr)
    mod.load_core(update)
    if update:
        if not modules_to_install and not modules_to_uninstall:
            mod.update([], False)
        elif modules_to_install:
            mod.update(modules_to_install, False)
        elif modules_to_uninstall:
            mod.load_all()
            mod.update(modules_to_uninstall, True)
    else:
        mod.load_all()


def run():
    http.init_routers(globalvars.flask_app)
    # globalvars.flask_app.run(host="0.0.0.0")
    # return
    config = hypercorn.Config()
    config.bind = "0.0.0.0:5000"
    config.accesslog = "-"
    config.errorlog = "-"
    asyncio.run(hypercorn.asyncio.serve(globalvars.flask_app, config))
