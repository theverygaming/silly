import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload


@app.route("/webclient2/view/form/<view_id>")
def webclient2_form(view_id):
    view = {
        "model": "xmlid",
        "fields": [
            {
                "name": "ID",
                "field": "id",
            },
            {
                "name": "XML ID",
                "field": "xmlid",
            },
            {
                "name": "Model Name",
                "field": "model_name",
            },
            {
                "name": "Model ID",
                "field": "model_id",
            },
            {
                "name": "ID (dupe lol)",
                "field": "id",
            },
        ],
    }

    env_lock.acquire()
    try:
        read_vals = list(set([field["field"] for field in view["fields"]]))

        return env["template"].render(
            "template_render_view_form",
            {
                "view": view,
                "fields": view["fields"],
                "data": env[view["model"]].browse(int(request.args["id"])).read(read_vals)[0],
            },
        )
    finally:
        env_lock.release()
