import threading
import flask

env = None
env_lock = threading.Lock()
flask_app = flask.Flask("silly", static_folder=None)
