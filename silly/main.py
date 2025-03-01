import threading
import sqlite3
import sillyorm
import flask
from . import renderer, modload, xmlids, http


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


def init(sql_connection):
    global env
    env = CustomEnvironment(sql_connection.cursor())
    env.register_model(renderer.Template)
    env.register_model(xmlids.XMLId)


def run():
    modload.load_all(env)
    env.init_tables()
    modload.load_all_data(env)
    http.init_routers(flask_app)
    flask_app.run(host="0.0.0.0")
