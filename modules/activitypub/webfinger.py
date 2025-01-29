import re
import json
from pathlib import PurePath
from flask import request
from silly.main import env, env_lock
import silly.modload
from silly import http

RE_SERVER_URL = r"fedi\.theverygaming\.furrypri\.de"

class ActivityPubWebfinger(http.Router):
    @http.route("/.well-known/webfinger")
    def well_known_webfinger(self):
        req_resource = request.args.get("resource")

        match = re.match(rf"acct:(?P<name>[^@]+)@{RE_SERVER_URL}", req_resource)
        if match is not None:
            name = match.group("name")
            print(f"requested actor: {name}")
            env_lock.acquire()
            try:
                actor = env["activitypub_actor"].search([("username", "=", name)])
                return actor.gen_webfinger_json()
            finally:
                env_lock.release()
