from silly.globalvars import env, env_lock
from silly import http

class ActivityPubRoutes(http.Router):
    @http.route("/")
    def index(self):
        env_lock.acquire()
        try:
            return env["template"].render("template_index", {})
        finally:
            env_lock.release()


    @http.route("/users")
    def users(self):
        env_lock.acquire()
        try:
            actors = env["activitypub_actor"].search([])
            return env["template"].render(
                "template_users",
                {
                    "userlist": [
                        {
                            "username": a.username,
                            "url": f"https://fedi.theverygaming.furrypri.de/users/{a.username}",
                        }
                        for a in actors
                    ]
                },
            )
        finally:
            env_lock.release()
