from silly import http


class ActivityPubRoutes(http.Router):
    @http.route("/")
    def index(self, request):
        return request.env["template"].render_html_resp("activitypub.template_index", {})

    @http.route("/users")
    def users(self, request):
        actors = request.env["activitypub_actor"].search([])
        return request.env["template"].render_html_resp(
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
