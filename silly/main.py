import logging
import flask
import pathlib
from . import modload, mod, http, globalvars

_logger = logging.getLogger(__name__)

def init(sql_connection, modules_to_install=[], modules_to_uninstall=[], update=False):
    if modules_to_install and modules_to_uninstall:
        raise Exception("can't install and uninstall stuff at the same time")
    _logger.info("silly version [...] starting")
    modload.add_module_paths([str(pathlib.Path(__file__).parent / "modules")])
    cursor = sql_connection.cursor()
    mod.load_core(cursor, update)
    if update:
        if not modules_to_install and not modules_to_uninstall:
            mod.update([], False)
        elif modules_to_install:
            mod.update(modules_to_install, False)
        elif modules_to_uninstall:
            mod.load_all(cursor)
            mod.update(modules_to_uninstall, False)
    else:
        mod.load_all(cursor)


def run():
    http.init_routers(globalvars.flask_app)
    globalvars.flask_app.run(host="0.0.0.0")
