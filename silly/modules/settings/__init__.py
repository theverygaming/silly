from . import models


def module_onload(env):
    env.register_model(models.Setting)
