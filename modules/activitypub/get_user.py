import logging
import re
import json
from pathlib import PurePath
from flask import request, Response
from silly.main import env, env_lock
import silly.modload
from silly import http

_logger = logging.getLogger(__name__)

class ActivityPubUser(http.Router):
    @http.route("/users/<username>")
    def get_profile(self, username):
        if request.accept_mimetypes["text/html"]:
            _logger.info("requested profile page (HTML) for: %s", username)
            env_lock.acquire()
            try:
                actor = env["activitypub_actor"].search([("username", "=", username)])
                return f"this would be a profile page for '{actor.username}'"
            finally:
                env_lock.release()
        elif request.accept_mimetypes["application/activity+json"]:
            _logger.info("requested profile (JSON) for: %s", username)
            env_lock.acquire()
            try:
                actor = env["activitypub_actor"].search([("username", "=", username)])
                return Response(
                    json.dumps(actor.gen_actor_json()), mimetype="application/activity+json"
                )
            finally:
                env_lock.release()


    @http.route("/users/<username>/inbox", methods=["GET", "POST"])
    def get_profile_inbox(self, username):
        if request.accept_mimetypes["text/html"]:
            _logger.info("requested inbox page (HTML) for: %s", username)
            return "no HTML inbox display for u :3c"
        else:
            _logger.info("requested inbox (JSON) for: %s", username)
            _logger.info("request data: %s", repr(request.data))
            rjson = request.get_json()
            _logger.info("request JSON: %s", repr(rjson))
            if rjson["type"] == "Delete":
                _logger.info("cache invalidation request for %s", repr(rjson['object']))
                return Response(
                    "404 not found", status=404
                )  # spec says if it doesn't exist we return 404
            if rjson["type"] == "Create":
                _logger.info("creation request for %s", repr(rjson['object']))
