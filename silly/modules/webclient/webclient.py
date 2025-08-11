import json
from pathlib import PurePath
import silly.modload
import sillyorm

from silly import http
from silly.modules.jsonrpc.routes import JSONRPCRoutes


class WebclientRoutes(http.Router):
    @http.route("/webclient/")
    def webclient(self, request):

        importmap = {"imports": {"@preact": "https://esm.sh/preact@10.26.4"}}

        for file in silly.modload.staticfiles:
            if not file.startswith("js/"):
                continue
            filep = PurePath(file)
            p = filep.parent.relative_to("js/") / filep.name
            importmap["imports"][f"@{str(p.with_suffix(''))}"] = "/static/js/" + str(p)

        return request.env["core.template"].render_html_resp(
            "webclient.template_test2",
            {
                "importmap": json.dumps(importmap),
            },
        )
        # TODO: error page


class InheritJSONRPCRoutes(JSONRPCRoutes):
    def jsonrpc_conv_type(self, env, val):
        ret = super().jsonrpc_conv_type(env, val)
        if isinstance(val, sillyorm.model.Model):
            ret["spec"] = env[val._name].webclient_model_spec()
        return ret
