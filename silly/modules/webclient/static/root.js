import { Component, useState, App, loadFile, whenReady, reactive } from "@odoo/owl";
import { Counter } from "@counter/counter";
import { ErrorHandler } from "@tools/errorHandler"


class Root extends Component {
    static components = { ErrorHandler, Counter };
    static template = "root"

    setup() {
        this.state = useState({ total: 0, errors: this.env.errors });
    }

    addTotal(amount) {
        this.state.total += amount;
    }
}

const templates = await Promise.all([
    loadFile("/static/xml/counter/counter.xml"),
    loadFile("/static/xml/tools/errorHandler.xml"),
    loadFile("/static/xml/root.xml"),
]);

await whenReady()

const env = {
    errors: reactive([]),
};

const rootApp = new App(Root, { name: "Owl App", env });
for (const template of templates) {
    rootApp.addTemplates(template);
}

await rootApp.mount(document.body);


window.addEventListener("error", async function (ev) {
    console.log(ev);
    env.errors.push(`err event: ${ev}`);
});

window.addEventListener("unhandledrejection", async function (ev) {
    console.log(ev);
    // TODO
});


async function jsonrpc(url, method, id, params) {
    const resp = await fetch(url, {
        method: "POST",
        body: JSON.stringify({
            jsonrpc: "2.0",
            id: id,
            method: method,
            params: params
        }),
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
    });
    return (await resp.json()).result;
}

console.log(jsonrpc("/webclient/jsonrpc", "get_view", 0, {
    model: "some_model",
}));
