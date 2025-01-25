import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload

from . import view

@app.route("/webclient2/view/<view_id>")
def webclient2_render_view(view_id):
    env_lock.acquire()
    try:
        return view.render_view(env, view_id, request.args)
    finally:
        env_lock.release()
