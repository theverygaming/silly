import json
from pathlib import PurePath
from flask import request
from silly.main import app, env, env_lock
import silly.modload


@app.route("/webclient")
def webclient():

    importmap = {"imports": {"@odoo/owl": "https://unpkg.com/@odoo/owl@2.3.0/dist/owl.es.js"}}

    for file in silly.modload.staticfiles:
        if not file.startswith("js/"):
            continue
        filep = PurePath(file)
        p = filep.parent.relative_to("js/") / filep.name
        importmap["imports"][f"@{str(p.with_suffix(''))}"] = "/static/js/" + str(p)

    env_lock.acquire()
    try:
        return env["template"].render(
            "template_test2",
            {
                "importmap": json.dumps(importmap),
            },
        )
    # TODO: error page
    finally:
        env_lock.release()


@app.route("/webclient/jsonrpc", methods=["POST"])
def jsonrpc():
    rdata = json.loads(request.data)
    rpc_id = rdata["id"]
    rpc_method = rdata["method"]
    rpc_params = rdata["params"]
    match rpc_method:
        case "get_view":
            env_lock.acquire()
            try:
                view = env["view"].search([("model_name", "=", rpc_params["model"])])
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "component_name": view.type_id.component_name,
                        "xml": view.xml,
                    },
                }
            finally:
                env_lock.release()
        case "search_read":
            env_lock.acquire()
            try:
                data = env[rpc_params["model"]].search(rpc_params["domain"])
                return {
                    "jsonrpc": "2.0",
                    "result": data.read(rpc_params["fields"]),
                }
            finally:
                env_lock.release()
        case "browse_read":
            env_lock.acquire()
            try:
                data = env[rpc_params["model"]].browse(rpc_params["ids"])
                return {
                    "jsonrpc": "2.0",
                    "result": data.read(rpc_params["fields"]),
                }
            finally:
                env_lock.release()
        case "browse_write":
            env_lock.acquire()
            try:
                data = env[rpc_params["model"]].browse(rpc_params["ids"])
                data.write(rpc_params["data"])
                return {
                    "jsonrpc": "2.0",
                    "result": True,
                }
            finally:
                env_lock.release()
