import logging
from silly import http, mod

_logger = logging.getLogger(__name__)


class ModulemanagerRoutes(http.Router):
    @http.route("/modulemanager/manage/{op:str}/{module:str}")
    def manage(self, request):
        op = request.path_params["op"]
        module = request.path_params["module"]
        if op not in ["install", "uninstall"]:
            return "invalid op :("
        _logger.info("%s operation on module %s", op, module)
        mod.update([module], uninstall=op == "uninstall")
        return "am on it :3"
