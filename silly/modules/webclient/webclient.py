import json
from pathlib import PurePath
import silly.modload
import sillyorm

from silly import http


class WebclientRoutes(http.Router):
    @http.route("/webclient/")
    def webclient(self, request):
        return request.env["core.template"].render_html_resp(
            "webclient.index",
            {
                "mainmenu": False,
            },
        )
        # TODO: error page
