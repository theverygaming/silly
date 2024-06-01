from . import activitypub, models


def module_onload(env):
    env.register_model(models.Actor)
