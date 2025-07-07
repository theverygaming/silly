from silly import http


class ActivityPubRoutes(http.Router):
    @http.route("/")
    def index(self, env):
        return env["template"].render("activitypub.template_index", {})

    @http.route("/users")
    def users(self, env):
        actors = env["activitypub_actor"].search([])
        return env["template"].render(
            "activitypub.template_users",
            {
                "userlist": [
                    {
                        "username": a.username,
                        "url": (
                            f"https://vps-old.infra.theverygaming.furrypri.de/users/{a.username}"
                        ),
                    }
                    for a in actors
                ]
            },
        )
