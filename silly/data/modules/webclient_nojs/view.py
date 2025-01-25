views = {
    "some_list": {
        "type": "list",
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
        "form_view_id": "some_form",
    },
    "some_form": {
        "type": "form",
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
    },
}

def _render_view_form(env, view, params):
    read_vals = list(set([field["field"] for field in view["fields"]]))
    return env["template"].render(
        "template_render_view_form",
        {
            "view": view,
            "fields": view["fields"],
            "data": env[view["model"]].browse(int(params["id"])).read(read_vals)[0],
        },
    )

def _render_view_list(env, view, params):
    domain = []
    total_records = env[view["model"]].search_count(domain)

    # important: these offsets are meant for humans and start at 1
    offset_start = int(params.get("offset_start", 1))
    offset_end = int(params.get("offset_end", view["pagination"]["default_page_size"]))
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

def render_view(env, name, params):
    view = views[name]
    view_t_lookup = {
        "list": _render_view_list,
        "form": _render_view_form,
    }
    return view_t_lookup[view["type"]](env, view, params)
