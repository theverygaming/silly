import logging
import sillyorm
from flask import Flask
from . import renderer

env = None
app = Flask("silly")


@app.route("/")
def hello_world():
    # cursed: SQLite can't cope with objects shared between threads
    # we need locks
    env = sillyorm.Environment(sillyorm.dbms.sqlite.SQLiteConnection("test.db").cursor())
    env.register_model(renderer.Template)
    return env["template"].render("test", {})


def run_app():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.DEBUG
    )

    global env
    env = sillyorm.Environment(sillyorm.dbms.sqlite.SQLiteConnection("test.db").cursor())
    env.register_model(renderer.Template)

    env["template"].load_file("silly/templates/index.xml")

    app.run()
