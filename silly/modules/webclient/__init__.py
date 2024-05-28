from . import webclient, models

def module_onload(env):
    env.register_model(models.ViewType)
    env.register_model(models.View)

    views = env["view"].search([])
    if views is not None:
        views.delete()
    
    view_types = env["view_type"].search([])
    if view_types is not None:
        view_types.delete()

    vt_id = env["view_type"].create({
        "component_name": "somecomp"
    }).id

    env["view"].create({
        "model_name": "some_model",
        "type_id": vt_id,
        "xml": "hello world!"
    })
