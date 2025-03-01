from silly.modules.webclient_nojs.view import views

views.update(
    {
        "settings_list": {
            "type": "list",
            "model": "settings_setting",
            "fields": [
                {
                    "name": "Key",
                    "field": "key",
                },
                {
                    "name": "Value",
                    "field": "value",
                },
            ],
            "pagination": {
                "default_page_size": 5,
            },
            "form_view_id": "settings_form",
        },
        "settings_form": {
            "type": "form",
            "model": "settings_setting",
            "fields": [
                {
                    "name": "Key",
                    "field": "key",
                    "type": "str",
                },
                {
                    "name": "Value",
                    "field": "value",
                    "type": "str",
                    "widget": {
                        "type": "textarea",
                    },
                },
            ],
            "actions": [],
        },
    }
)
