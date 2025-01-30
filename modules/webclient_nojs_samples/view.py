from silly.modules.webclient_nojs.view import views

views.update({
    "some_list": {
        "type": "list",
        "model": "xmlid",
        "fields": [
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
                "name": "XML ID (Dupe lol)",
                "field": "xmlid",
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
    "test_model_list": {
        "type": "list",
        "model": "test_model",
        "fields": [
            {
                "name": "ID",
                "field": "id",
            },
            {
                "name": "Integer",
                "field": "integer",
            },
            {
                "name": "Float",
                "field": "float",
            },
            {
                "name": "String",
                "field": "string",
            },
            {
                "name": "Text",
                "field": "text",
            },
            {
                "name": "Date",
                "field": "date",
            },
            {
                "name": "Datetime",
                "field": "datetime",
            },
            {
                "name": "Boolean",
                "field": "boolean",
            },
            {
                "name": "Selection",
                "field": "selection",
            },
        ],
        "pagination": {
            "default_page_size": 5,
        },
        "form_view_id": "test_model_form",
    },
    "test_model_form": {
        "type": "form",
        "model": "test_model",
        "fields": [
            {
                "name": "ID",
                "field": "id",
                "type": "int",
                "readonly": True,
            },
            {
                "name": "Integer",
                "field": "integer",
                "type": "int",
            },
            {
                "name": "Float",
                "field": "float",
                "type": "float",
            },
            {
                "name": "String",
                "field": "string",
                "type": "str",
            },
            {
                "name": "Text",
                "field": "text",
                "type": "str",
                "widget": {
                    "type": "textarea",
                },
            },
            {
                "name": "Date",
                "field": "date",
                "type": "date",
            },
            {
                "name": "Datetime",
                "field": "datetime",
                "type": "datetime",
            },
            {
                "name": "Boolean",
                "field": "boolean",
                "type": "bool",
            },
            {
                "name": "Selection",
                "field": "selection",
                "type": "str",
                "widget": {
                    "type": "selection",
                    "options": [
                        "option 1",
                        "option 2",
                    ],
                },
            },
        ],
        "actions": [],
    },
})
