import logging
import threading
import sqlite3
import sillyorm
import flask
from . import renderer, modload


env = None
env_lock = threading.Lock()
app = flask.Flask("silly", static_folder=None)


@app.route("/static/<path:subpath>")
def static_serve(subpath):
    if subpath in modload.staticfiles:
        return flask.send_file(modload.staticfiles[subpath])
    return "404"

def init(sql_connection):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.DEBUG
    )
    global env
    env = sillyorm.Environment(sql_connection.cursor())
    env.register_model(renderer.Template)


def run():
    app.run(host="0.0.0.0")
