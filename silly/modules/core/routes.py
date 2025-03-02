import flask
from silly import http, modload


class CoreRoutes(http.Router):
    @http.route("/static/<path:subpath>")
    def static_serve(self, subpath):
        if subpath in modload.staticfiles:
            return flask.send_file(modload.staticfiles[subpath])
        return "404"
