import re
import json
from pathlib import PurePath
from flask import request, Response
from silly.main import app, env, env_lock
import silly.modload

RE_SERVER_URL = r"fedi\.theverygaming\.furrypri\.de"


@app.route("/@<username>")
def get_profile(username):
    if request.accept_mimetypes["text/html"]:
        print(f"requested profile page (HTML) for: {username}")
        env_lock.acquire()
        try:
            actor = env["activitypub_actor"].search([("username", "=", username)])
            return f"this would be a profile page for @{actor.username}"
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
