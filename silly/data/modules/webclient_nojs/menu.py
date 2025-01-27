import re
import urllib.parse

menus = {
    "some_app": {
        "label": "Some App",
        "url": "/webclient2/view/some_list"
    },
}

def show_menu(env):
    return env["template"].render(
        "webclient_nojs.menu",
        {
            "menus": menus,
        },
    )
