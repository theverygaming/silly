from . import menu, view, models


def module_onload(env):
    env.register_model(models.TestModel)
