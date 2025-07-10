import logging
import re
import json
from pathlib import PurePath
import starlette.responses
import silly.modload
from silly import http

_logger = logging.getLogger(__name__)


class ActivityPubUser(http.Router):
    @http.route("/users/{username:str}")
    def get_profile(self, request):
        username = request.path_params["username"]
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            _logger.info("requested profile page (HTML) for: %s", username)
            actor = request.env["activitypub_actor"].search([("username", "=", username)])
            return f"this would be a profile page for '{actor.username}'"
        elif "application/activity+json" in accept:
            _logger.info("requested profile (JSON) for: %s", username)
            actor = request.env["activitypub_actor"].search([("username", "=", username)])
            return starlette.responses.JSONResponse(
                json.dumps(actor.gen_actor_json()), media_type="application/activity+json"
            )

    @http.route("/users/{username:str}/inbox", methods=["GET", "POST"], with_env=False)
    async def get_profile_inbox(self, request):
        username = request.path_params["username"]
        _logger.info("requested inbox (JSON) for: %s", username)
        rjson = await request.json()
        _logger.info("request JSON: %s", repr(rjson))
        if rjson["type"] == "Delete":
            _logger.info("cache invalidation request for %s", repr(rjson["object"]))
            return 404  # spec says if it doesn't exist we return 404
        if rjson["type"] == "Create":
            _logger.info("creation request for %s", repr(rjson["object"]))
