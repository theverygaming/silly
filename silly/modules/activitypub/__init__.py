from . import activitypub, models, webfinger, get_user, routes


def module_onload(env):
    env.register_model(models.Actor)
