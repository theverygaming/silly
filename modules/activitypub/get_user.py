import re
import json
from pathlib import PurePath
from flask import request, Response
from silly.main import env, env_lock
import silly.modload
from silly import http

class ActivityPubUser(http.Router):
    @http.route("/users/<username>")
    def get_profile(self, username):
        if request.accept_mimetypes["text/html"]:
            print(f"requested profile page (HTML) for: {username}")
            env_lock.acquire()
            try:
                actor = env["activitypub_actor"].search([("username", "=", username)])
                return f"this would be a profile page for '{actor.username}'"
            finally:
                env_lock.release()
        elif request.accept_mimetypes["application/activity+json"]:
            print(f"requested profile (JSON) for: {username}")
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
            print(f"requested inbox page (HTML) for: {username}")
            return "no HTML inbox display for u :3c"
        else:
            print(f"requested inbox (JSON) for: {username}")
            print(request.data)
            rjson = request.get_json()
            print(rjson)
            if rjson["type"] == "Delete":
                print(f"cache invalidation request for {rjson['object']}")
                return Response(
                    "404 not found", status=404
                )  # spec says if it doesn't exist we return 404
            if rjson["type"] == "Create":
                print(f"creation request for {rjson['object']}")
