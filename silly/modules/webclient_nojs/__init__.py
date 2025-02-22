from . import routes, models


def module_onload(env):
    env.register_model(models.View)
