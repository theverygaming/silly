import json
from pathlib import PurePath
from flask import request
from silly.globalvars import env, env_lock
import silly.modload

from silly import http


class WebclientRoutes(http.Router):
    @http.route("/webclient/")
    def webclient(self):

        importmap = {"imports": {"@preact": "https://esm.sh/preact@10.26.4"}}

        for file in silly.modload.staticfiles:
            if not file.startswith("js/"):
                continue
            filep = PurePath(file)
            p = filep.parent.relative_to("js/") / filep.name
            importmap["imports"][f"@{str(p.with_suffix(''))}"] = "/static/js/" + str(p)

        env_lock.acquire()
        try:
            return env["template"].render(
                "webclient.template_test2",
                {
                    "importmap": json.dumps(importmap),
                },
            )
        # TODO: error page
        finally:
            env_lock.release()

    @http.route("/webclient/jsonrpc", methods=["POST"])
    def jsonrpc(self):
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
