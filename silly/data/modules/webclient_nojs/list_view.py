import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload


@app.route("/webclient2/view/list/<view_id>")
def webclient2_list(view_id):
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
        "pagination": {
            "default_page_size": 50,
        },
        "form_view_id": "some_form_view",
    }

    env_lock.acquire()
    try:
        domain = []
        total_records = env[view["model"]].search_count(domain)

        # important: these offsets are meant for humans and start at 1
        offset_start = int(request.args.get("offset_start", 1))
        offset_end = int(request.args.get("offset_end", view["pagination"]["default_page_size"]))
        if offset_end > total_records:
            offset_end = total_records
        if offset_start > offset_end:
            offset_start = offset_end

        read_vals = list(set([field["field"] for field in view["fields"]]))

        return env["template"].render(
            "template_render_view_list",
            {
                "view": view,
                "fields": view["fields"],
                "rows": env[view["model"]].search(domain, offset=offset_start-1, limit=offset_end - (offset_start-1)).read(read_vals),
                "pagination": {
                    "offset_start": offset_start,
                    "offset_end": offset_end,
                    "total_records": total_records,
                }
            },
        )
    finally:
        env_lock.release()
