import json
from pathlib import PurePath
from silly.main import app, env, env_lock
import silly.modload

@app.route("/webclient")
def webclient():

    importmap = {
        "imports": {}
    }

    for file in silly.modload.staticfiles:
        if not file.startswith("js/"):
            continue
        filep = PurePath(file)
        p = filep.parent.relative_to("js/") / filep.name
        importmap["imports"][f"@{str(p.with_suffix(''))}"] = "/static/js/" + str(p)

    env_lock.acquire()
    try:
        return env["template"].render("test2", {
            "importmap": json.dumps(importmap),
        })
    finally:
        env_lock.release()
