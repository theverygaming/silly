from . import webclient, models


def module_onload(env):
    env.register_model(models.ViewType)
    env.register_model(models.View)
