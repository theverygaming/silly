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


@app.route("/")
def hello_world():
    env_lock.acquire()
    try:
        return env["template"].render("test", {})
    finally:
        env_lock.release()


class CustomSQLiteConnection(sillyorm.dbms.sqlite.SQLiteConnection):
    def __init__(self, *args, **kwargs):
        self._conn = sqlite3.connect(*args, **kwargs)


def run_app():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.DEBUG
    )

    global env
    # env = sillyorm.Environment(
    #    sillyorm.dbms.postgresql.PostgreSQLConnection(
    #        "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #    ).cursor()
    # )
    env = sillyorm.Environment(CustomSQLiteConnection("test.db", check_same_thread=False).cursor())
    env.register_model(renderer.Template)

    modload.set_module_paths(["silly/modules"])

    modload.load_module("webclient", env)

    modload.load_datafile(env, "silly/templates/index.xml")

    app.run()
