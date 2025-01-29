import re
import urllib.parse

views = {}

def _render_view_form(env, view, view_name, params, action_view_msgs=[]):
    read_vals = list(set([field["field"] for field in view["fields"]]))
    if len(read_vals) != len(view["fields"]):
        raise Exception("duplicate fields in view")
    data = env[view["model"]].browse(int(params["id"])).read(read_vals)[0]

    for field in view["fields"]:
        data[field["field"]] = _conv_type_read_form(data[field["field"]], field["type"])

    return env["template"].render(
        "webclient_nojs.view_form",
        {
            "view": view,
            "fields": view["fields"],
            "data": data,
            "action_view_msgs": action_view_msgs,
        },
    )

def _conv_type_write_form(val, t):
    match t:
        case "int":
            return int(val)
        case "str":
            return str(val)
    raise Exception(f"unknown type {t}")

def _conv_type_read_form(val, t):
    return str(val)

def _form_handle_post(env, view, view_name, params, post_params):
    match post_params["type"]:
        case "save":
            raw_field_vals = {int(m.group(1)): v for k, v in post_params.items() if (m := re.match(r"^field_(\d+)$", k)) is not None}
            vals = {view["fields"][k]["field"]: _conv_type_write_form(v, view["fields"][k]["type"]) for k, v in raw_field_vals.items() if not view["fields"][k].get("readonly", False)}
            # remove fields we can't write
            for k in vals.copy():
                if k in ["id"]:
                    del vals[k]

            env[view["model"]].browse(int(params["id"])).write(vals)
            return {
                "view_msgs": ["saved successfully"],
            }
        case "action":
            action = view["actions"][int(post_params["action_id"])]
            if action["per-record"]:
                rec = env[view["model"]].browse(int(params["id"]))
                return action["fn"](env, rec)
            return action["fn"](env)


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
    
    order_by = int(x) if (x := params.get("order_by")) is not None else x
    order_asc = (not x == "descending") if (x := params.get("order_asc")) is not None else True
    if order_by is not None and (order_by < 0 or order_by >= len(view["fields"])):
        order_by = None

    read_vals = list(set([field["field"] for field in view["fields"]]))

    def _gen_url_params(url_params):
        return urllib.parse.urlencode(url_params)

    return env["template"].render(
        "webclient_nojs.view_list",
        {
            "view": view,
            "fields": view["fields"],
            "rows": env[view["model"]].search(
                domain,
                offset=offset_start-1,
                limit=offset_end - (offset_start-1),
                order_by=view["fields"][order_by]["field"] if order_by is not None else None,
                order_asc=order_asc
            ).read(read_vals),
            "pagination": {
                "offset_start": offset_start,
                "offset_end": offset_end,
                "total_records": total_records,
            },
            "sorting": {
                "order_by": order_by,
                "order_asc": order_asc,
            },
            "request_params_get": params,
            "active_url": f"/webclient2/view/{view_name}",
            "gen_url_params": _gen_url_params,
        },
    )

def render_view(env, name, params, **kwargs):
    view = views[name]
    view_t_lookup = {
        "list": _render_view_list,
        "form": _render_view_form,
    }
    return view_t_lookup[view["type"]](env, view, name, params, **kwargs)

def handle_post(env, name, params, post_params):
    view = views[name]
    view_t_lookup = {
        "form": _form_handle_post,
    }
    action_return = view_t_lookup[view["type"]](env, view, name, params, post_params)
    if action_return is None:
        return render_view(env, name, params)
    if action_return.get("view_msgs") is not None:
        return render_view(env, name, params, action_view_msgs=action_return["view_msgs"])
    raise Exception(f"could not parse action return {action_return}")
