import logging
import re
import json
from pathlib import PurePath
from flask import request
import silly.modload
from silly import http

_logger = logging.getLogger(__name__)

RE_SERVER_URL = r"fedi\.theverygaming\.furrypri\.de"


class ActivityPubWebfinger(http.Router):
    @http.route("/.well-known/webfinger")
    def well_known_webfinger(self, env):
        req_resource = request.args.get("resource")

        match = re.match(rf"acct:(?P<name>[^@]+)@{RE_SERVER_URL}", req_resource)
        if match is not None:
            name = match.group("name")
            _logger.info("requested actor: %s", name)
            actor = env["activitypub_actor"].search([("username", "=", name)])
            return actor.gen_webfinger_json()
