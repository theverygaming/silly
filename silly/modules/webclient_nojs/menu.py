import re
import urllib.parse

menus = []


def show_menu(env):
    return env["template"].render(
        "webclient_nojs.menu",
        {
            "menus": menus,
        },
    )
