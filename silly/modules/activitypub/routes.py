from silly.main import app, env, env_lock


@app.route("/")
def index():
    env_lock.acquire()
    try:
        return env["template"].render("index", {})
    finally:
        env_lock.release()


@app.route("/users")
def users():
    env_lock.acquire()
    try:
        actors = env["activitypub_actor"].search([])
        return env["template"].render(
            "users",
            {
                "userlist": [
                    {
                        "username": a.username,
                        "url": (
                            f'https://fedi.theverygaming.furrypri.de/users/{a.username}'
                        ),
                    }
                    for a in actors
                ]
            },
        )
    finally:
        env_lock.release()
