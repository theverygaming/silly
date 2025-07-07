import logging
import re
from silly import http
from silly.modules.webfinger.webfinger import Webfinger

_logger = logging.getLogger(__name__)


class ActivityPubWebfinger(Webfinger):
    def webfinger_handle(self, env, resource, req):
        match = re.match(rf"acct:(?P<name>[^@]+)@(?P<server>.+)", resource)
        if match is None:
            return super().webfinger_handle(env, resource, req)
        name = match.group("name")
        server = match.group("server")
        if server != "vps-old.infra.theverygaming.furrypri.de":
            return http.Response(code=404)
        _logger.info("requested actor: @%s@%s", name, server)
        actor = env["activitypub_actor"].search([("username", "=", name)])
        if not actor:
            return http.Response(code=404)
        return actor.gen_webfinger_json()
