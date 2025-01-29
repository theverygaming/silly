from silly.modules.webclient_nojs.view import views

views.update({
    "some_list": {
        "type": "list",
        "model": "xmlid",
        "fields": [
            {
                "name": "ID",
                "field": "id",
            },
            {
                "name": "XML ID",
                "field": "xmlid",
            },
            {
                "name": "Model Name",
                "field": "model_name",
            },
            {
                "name": "Model ID",
                "field": "model_id",
            },
            {
                "name": "ID (dupe lol)",
                "field": "id",
            },
        ],
        "pagination": {
            "default_page_size": 5,
        },
        "form_view_id": "some_form",
    },
    "some_form": {
        "type": "form",
        "model": "xmlid",
        "fields": [
            {
                "name": "ID",
                "field": "id",
                "type": "str",
            },
            {
                "name": "XML ID",
                "field": "xmlid",
                "type": "str",
            },
            {
                "name": "Model Name",
                "field": "model_name",
                "type": "str",
                "widget": {
                    "type": "textarea",
                },
                "readonly": True,
            },
            {
                "name": "Model ID",
                "field": "model_id",
                "type": "int",
                "readonly": True,
            }
        ],
        "actions": [
            {
                "fn": lambda env, rec: None,
                "per-record": True,
                "label": "something",
            },
            {
                "fn": lambda env, rec: {"view_msgs": [f"rec: {rec}"]},
                "per-record": True,
                "label": "Another Thing (Form Action)",
            },
            {
                "fn": lambda env: {"view_msgs": [f"hello world!"]},
                "per-record": False,
                "label": "Another Thing (Form Action) -- NOT per-record",
            },
        ],
    },
})
