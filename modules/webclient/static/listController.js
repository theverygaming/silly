import { Component, useState } from "@odoo/owl";
import { jsonrpc } from "@jsonrpc";
import { ViewHelper } from "@viewHelper";


export class ListController extends Component {
    static template = "listController";

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

            this.viewhelper.searchRecords(this.state.fields).then((res) => {
                console.log(res);
                this.state.data = res;
            });
        });
    }
}
