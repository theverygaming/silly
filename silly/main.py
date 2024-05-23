import logging
import threading
import sqlite3
import sillyorm
import flask
from . import renderer

env = None
env_lock = threading.Lock()
app = flask.Flask("silly")

@app.route('/static/<path:path>')
def send_report(path):
    return flask.send_from_directory('silly/static', path)

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
    #env = sillyorm.Environment(
    #    sillyorm.dbms.postgresql.PostgreSQLConnection(
    #        "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #    ).cursor()
    #)
    env = sillyorm.Environment(CustomSQLiteConnection("test.db", check_same_thread=False).cursor())
    env.register_model(renderer.Template)

    env["template"].load_file("silly/templates/index.xml")

    app.run()
