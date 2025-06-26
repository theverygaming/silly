import json
from pathlib import PurePath
from flask import request
import silly.modload

from silly import http


class WebclientRoutes(http.Router):
    @http.route("/webclient/")
    def webclient(self, env):

        importmap = {"imports": {"@preact": "https://esm.sh/preact@10.26.4"}}

        for file in silly.modload.staticfiles:
            if not file.startswith("js/"):
                continue
            filep = PurePath(file)
            p = filep.parent.relative_to("js/") / filep.name
            importmap["imports"][f"@{str(p.with_suffix(''))}"] = "/static/js/" + str(p)

        return env["template"].render(
            "webclient.template_test2",
            {
                "importmap": json.dumps(importmap),
            },
        )
        # TODO: error page

    @http.route("/webclient/jsonrpc", methods=["POST"])
    def jsonrpc(self, env):
        rdata = json.loads(request.data)
        rpc_id = rdata["id"]
        rpc_method = rdata["method"]
        rpc_params = rdata["params"]
        match rpc_method:
            case "get_view":
                view = env["view"].search([("model_name", "=", rpc_params["model"])])
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "component_name": view.type_id.component_name,
                        "xml": view.xml,
                    },
                }
            case "search_read":
                data = env[rpc_params["model"]].search(rpc_params["domain"])
                return {
                    "jsonrpc": "2.0",
                    "result": data.read(rpc_params["fields"]),
                }
            case "browse_read":
                data = env[rpc_params["model"]].browse(rpc_params["ids"])
                return {
                    "jsonrpc": "2.0",
                    "result": data.read(rpc_params["fields"]),
                }
            case "browse_write":
                data = env[rpc_params["model"]].browse(rpc_params["ids"])
                data.write(rpc_params["data"])
                return {
                    "jsonrpc": "2.0",
                    "result": True,
                }
