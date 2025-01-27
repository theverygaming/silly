import logging
import threading
import sqlite3
import sillyorm
import flask
from . import renderer, modload, xmlids, http


env = None
env_lock = threading.Lock()
app = flask.Flask("silly", static_folder=None)


@app.route("/static/<path:subpath>")
def static_serve(subpath):
    if subpath in modload.staticfiles:
        return flask.send_file(modload.staticfiles[subpath])
    return "404"

class CustomEnvironment(sillyorm.Environment):
    def xmlid_lookup(self, model, xmlid):
        return self["xmlid"].lookup(model, xmlid)

def init(sql_connection):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.DEBUG
    )
    global env
    env = CustomEnvironment(sql_connection.cursor())
    env.register_model(renderer.Template)
    env.register_model(xmlids.XMLId)
    env["template"]._table_init()  # a little cursed but does work i guess


def run():
    modload.load_all(env)
    env.init_tables()
    modload.load_all_data(env)
    http.init_routers(app)
    app.run(host="0.0.0.0")
