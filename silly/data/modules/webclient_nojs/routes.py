import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload

from . import view

@app.route("/webclient2/view/<view_id>", methods=["GET", "POST"])
def webclient2_render_view(view_id):
    env_lock.acquire()
    try:
        match request.method:
            case "GET":
                return view.render_view(env, view_id, request.args)
            case "POST":
                return view.handle_post(env, view_id, request.args, request.form)
    finally:
        env_lock.release()
