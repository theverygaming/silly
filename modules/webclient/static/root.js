import { Component, useState, App, loadFile, whenReady, reactive } from "@odoo/owl";
import { Counter } from "@counter/counter";
import { ErrorHandler } from "@tools/errorHandler"
import { FormController } from "@formController";
import { ListController } from "@listController";


class Root extends Component {
    static components = { ErrorHandler, Counter, FormController, ListController };
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
    loadFile("/static/xml/formController.xml"),
    loadFile("/static/xml/listController.xml"),
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
