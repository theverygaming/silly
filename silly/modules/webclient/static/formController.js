import { Component, useState } from "@odoo/owl";

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

export class FormController extends Component {
    static template = "formController";

    setup() {
        this.state = useState({ fields: [], data: [] });
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
        });

        jsonrpc("/webclient/jsonrpc", "search_read", 0, {
            model: "template",
            domain: [],
            fields: ["name", "xml"]
        }).then((res) => {
            console.log(res);
            this.state.data = res;
        });
    }
}
