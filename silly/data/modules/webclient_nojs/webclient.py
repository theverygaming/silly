import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload


@app.route("/webclient2")
def webclient2():
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

    read_vals = list(set([field["field"] for field in view["fields"]]))

    env_lock.acquire()
    try:
        return env["template"].render(
            "template_render_view_list",
            {
                "fields": view["fields"],
                "rows": env[view["model"]].search([]).read(read_vals),
            },
        )
    finally:
        env_lock.release()
