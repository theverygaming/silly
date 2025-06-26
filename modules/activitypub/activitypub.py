import json
from pathlib import PurePath
from flask import request
import silly.modload
from silly import http


class ActivityPubActivitypub(http.Router):
    @http.route("/activitypub")
    def activitypub(self, env):
        return env["template"].render(
            "webclient.template_test2",
            {},
        )
