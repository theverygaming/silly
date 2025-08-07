import json
from pathlib import PurePath
import silly.modload

from silly import http


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
