from . import activitypub, models, webfinger, get_user


def module_onload(env):
    env.register_model(models.Actor)
