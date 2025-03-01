import threading
import logging
import sillyorm
import flask
from . import modload, http, model

_logger = logging.getLogger(__name__)


env = None
env_lock = threading.Lock()
flask_app = flask.Flask("silly", static_folder=None)


@flask_app.route("/static/<path:subpath>")
def static_serve(subpath):
    if subpath in modload.staticfiles:
        return flask.send_file(modload.staticfiles[subpath])
    return "404"


class CustomEnvironment(sillyorm.Environment):
    def xmlid_lookup(self, model, xmlid):
        return self["xmlid"].lookup(model, xmlid)


def reload(cursor, modules_to_load):
    _logger.info("silly init stage 1 (load core module)")
    modload.unload_all()
    env_initial = CustomEnvironment(cursor)
    modload.add_module_paths(["silly/modules/"])
    modload.load_module("core")
    modload.load_all(env_initial)
    env_initial.init_tables()
    modload.load_all_data(env_initial)

    # TODO: figure out which modules to load

    _logger.info("unloading to prepare for init stage 2")
    modload.unload_all()
    
    _logger.info("silly init stage 2 (load core and everything else)")
    global env
    env = CustomEnvironment(cursor)
    modload.load_module("core")
    for mod in modules_to_load:
        modload.load_module(mod)
    modload.load_all(env)
    env.init_tables()
    modload.load_all_data(env)


def init(sql_connection, modules_to_load):
    reload(sql_connection.cursor(), modules_to_load)


def run():
    http.init_routers(flask_app)
    flask_app.run(host="0.0.0.0")
