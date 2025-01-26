import re
import urllib.parse

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
                "type": "text",
            },
            {
                "name": "XML ID",
                "field": "xmlid",
                "type": "text",
            },
            {
                "name": "Model Name",
                "field": "model_name",
                "type": "largetext",
            },
            {
                "name": "Model ID",
                "field": "model_id",
                "type": "text",
                "type_conv": "int",
            },
            {
                "name": "ID (dupe lol)",
                "field": "id",
                "type": "text",
            },
        ],
    },
}

def _render_view_form(env, view, view_name, params):
    read_vals = list(set([field["field"] for field in view["fields"]]))
    return env["template"].render(
        "template_render_view_form",
        {
            "view": view,
            "fields": view["fields"],
            "data": env[view["model"]].browse(int(params["id"])).read(read_vals)[0],
        },
    )

def _form_handle_post(env, view, view_name, params, post_params):
    if post_params["type"] == "save":
        def _conv_type(val, t):
            match t:
                case "int":
                    return int(val)
                case _:
                    return val
        field_hash_lookup_idx = {str(hash(str(field))): idx for idx, field in enumerate(view["fields"])}
        # TODO: fields that occour twice? whatever, will fix later
        vals = {view["fields"][(v_f_idx := field_hash_lookup_idx[m.group(1)])]["field"]: (_conv_type(v, view["fields"][v_f_idx]["type_conv"]) if "type_conv" in view["fields"][v_f_idx] else v) for k, v in post_params.items() if (m := re.match(r"^field_(-?\d+)$", k)) is not None}
        # remove fields we can't write
        for k in vals.copy():
            if k in ["id"]:
                del vals[k]

        env[view["model"]].browse(int(params["id"])).write(vals)

def _render_view_list(env, view, view_name, params):
    domain = []
    total_records = env[view["model"]].search_count(domain)

    # important: these offsets are meant for humans and start at 1
    offset_start = int(params.get("offset_start", 1))
    offset_end = int(params.get("offset_end", view["pagination"]["default_page_size"]))
    if offset_start < 1:
        offset_start = 1
    if offset_end < 1:
        offset_end = view["pagination"]["default_page_size"]
    if offset_end > total_records:
        offset_end = total_records
    if offset_start > offset_end:
        offset_start = offset_end

    read_vals = list(set([field["field"] for field in view["fields"]]))

    def _gen_url_params(url_params):
        return urllib.parse.urlencode(url_params)

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
            },
            "request_params_get": params,
            "active_url": f"/webclient2/view/{view_name}",
            "gen_url_params": _gen_url_params,
        },
    )

def render_view(env, name, params):
    view = views[name]
    view_t_lookup = {
        "list": _render_view_list,
        "form": _render_view_form,
    }
    return view_t_lookup[view["type"]](env, view, name, params)

def handle_post(env, name, params, post_params):
    view = views[name]
    view_t_lookup = {
        "form": _form_handle_post,
    }
    # TODO: some sort of thing to return warnings etc.
    view_t_lookup[view["type"]](env, view, name, params, post_params)
    return render_view(env, name, params)
