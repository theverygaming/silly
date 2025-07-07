from silly import http


class Webfinger(http.Router):
    def webfinger_handle(self, env, resource, req):
        return http.Response(code=400)

    @http.route("/.well-known/webfinger")
    def well_known_webfinger(self, env, resource=None, req=None):
        if resource is None:
            return http.Response(code=400)
        return self.webfinger_handle(env, resource, req)
