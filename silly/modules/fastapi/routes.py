import logging
import starlette
import fastapi
from silly import http

_logger = logging.getLogger(__name__)


class FastAPIRoutes(http.Router):
    def fastapi_app_defs(self):
        return []

    @http.routes
    def fastapi(self):
        routes = []
        for appdef in self.fastapi_app_defs():
            _logger.info(
                "processing app '%s' mountpoint: '%s'", appdef["title"], appdef["mountpoint"]
            )
            app = fastapi.FastAPI(title=appdef["title"], description=appdef["description"])
            for router in appdef["routers"]:
                app.include_router(router=router)
            routes.append(starlette.routing.Mount(appdef["mountpoint"], app))
        return routes
