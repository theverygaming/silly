from silly import http


class Webfinger(http.Router):
    def webfinger_handle(self, env, resource, req):
        return 400

    @http.route("/.well-known/webfinger")
    def well_known_webfinger(self, request):
        resource = request.query_params.get("resource")
        req = request.query_params.get("req")
        if resource is None:
            return 400
        return self.webfinger_handle(request.env, resource, req)
