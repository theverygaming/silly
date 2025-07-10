import starlette.responses
from silly import http, modload


class CoreRoutes(http.Router):
    @http.route("/static/{subpath:path}", with_env=False)
    def static_serve(self, request):
        subpath = request.path_params["subpath"]
        if subpath in modload.staticfiles:
            return starlette.responses.FileResponse(modload.staticfiles[subpath])
        return 404
