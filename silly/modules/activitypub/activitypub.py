import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload


@app.route("/activitypub")
def activitypub():
    env_lock.acquire()
    try:
        return env["template"].render(
            "test2",
            {},
        )
    finally:
        env_lock.release()
