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
            "default_page_size": 50,
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
                "type": "text",
            },
            {
                "name": "XML ID",
                "field": "xmlid",
                "type": "text",
            },
            {
                "name": "Model Name",
                "field": "model_name",
                "type": "largetext",
            },
            {
                "name": "Model ID",
                "field": "model_id",
                "type": "text",
                "type_conv": "int",
            },
            {
                "name": "ID (dupe lol)",
                "field": "id",
                "type": "text",
            },
        ],
    },
})
