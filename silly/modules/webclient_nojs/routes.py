import json
from pathlib import PurePath
from flask import request
from silly.main import env, env_lock
import silly.modload

from . import view
from . import menu

from silly.http import Router, route
import silly.http as http

class Webclient(Router):
    @http.route("/webclient2", methods=["GET"])
    def webclient2_home(self):
        env_lock.acquire()
        try:
            return menu.show_menu(env)
        finally:
            env_lock.release()

    @http.route("/webclient2/view/<view_id>", methods=["GET", "POST"])
    def webclient2_render_view(self, view_id):
        env_lock.acquire()
        try:
            match request.method:
                case "GET":
                    return view.render_view(env, view_id, request.args)
                case "POST":
                    return view.handle_post(env, view_id, request.args, request.form)
        finally:
            env_lock.release()
