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
                    # by default when ImmutableMultiDict (the type of request.form)
                    # has two values with the same it will return only the first key.
                    # We want different behavior, we want the last key
                    form_processed = {k: request.form.getlist(k)[-1] for k in request.form}
                    return view.handle_post(env, view_id, request.args, form_processed)
        finally:
            env_lock.release()
