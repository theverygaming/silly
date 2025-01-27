import json
from pathlib import PurePath
from flask import request
from silly.main import env, env_lock
import silly.modload
from silly import http

class ActivityPubActivitypub(http.Router):
    @http.route("/activitypub")
    def activitypub(self):
        env_lock.acquire()
        try:
            return env["template"].render(
                "template_test2",
                {},
            )
        finally:
            env_lock.release()
