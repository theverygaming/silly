import { Component, useState } from "@odoo/owl";
import { jsonrpc } from "@jsonrpc";
import { ViewHelper } from "@viewHelper";


export class FormController extends Component {
    static template = "formController";

    setup() {
        this.state = useState({ fields: [], data: [] });
        this.viewhelper = new ViewHelper("template");

        jsonrpc("/webclient/jsonrpc", "get_view", 0, {
            model: "some_model",
        }).then((res) => {
            console.log(res.xml);
            const parser = new DOMParser();
            const doc = parser.parseFromString(`<root>${res.xml}</root>`, "text/xml");
            console.log(doc);
            const fields = [];
            for (const node of doc.children[0].children) {
                console.log(node, node.nodeName, node.getAttribute("name"));
                for (const nodec of node.children) {
                    console.log(nodec);
                }
                if(node.nodeName === "field") {
                    fields.push(node.getAttribute("name"));
                }
            }
            console.log(fields);
            this.state.fields = fields;

            this.viewhelper.browseRecords(this.state.fields, [1]).then((res) => {
                console.log(res);
                this.state.data = res[0];
            });
        });
    }

    async btnSave(ev) {
        let vals = {}
        for (const node of ev.target.parentElement.children) {
            const name = node.name;
            if (!this.state.fields.includes(name)) {
                continue;
            }
            vals[name] = node.value;
        }
        await this.viewhelper.writeRecords(vals, [1]);
        console.log("saved", vals);
    }
}
