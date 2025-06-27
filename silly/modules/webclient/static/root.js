import { createElement, cloneElement, render, Component, toChildArray, Fragment } from "@preact";
import { env } from "@orm";

let view = await (await env.model("view").call("search", [[]], {limit: 1})).call("web_read", [["model_name", "type_id.component_name", "xml"]]);
console.log(view);
console.log(view.xml);

const parser = new DOMParser();
const doc = parser.parseFromString(view.xml, "application/xml");
if (doc.querySelector("parsererror")) {
    console.log("error while parsing");
}

class ListViewComponent extends Component {
    state = {
        records: [{id: 1, name: "this is record 1"}, {id: 2, name: "this is record 2"}],
    };

	render(props, state) {
        let headNode = toChildArray(props.children).find(child => child.type === "head");
        let rowNode = toChildArray(props.children).find(child => child.type === "row");

        // table head
        let thead = createElement("thead", {}, createElement("tr", {}, toChildArray(headNode.props.children).map(child => {
            return this.transformTableElements(child, null);
        })));

        // rows
        const rowTemplate = rowNode;
        const rows = state.records.map(record => {
            return this.transformTableElements(rowTemplate, record);
        });
        return createElement("table", { border: 1, onClick: () => {console.log("click");this.setState(prev => ({ records: prev.records.concat([{id: 123, name: "This is a dynamically added record"}]) }));} },
            thead,
            createElement("tbody", {}, rows),
        );
    }

    transformTableElements(node, record) {
        if (!node) {
            return null;
        }

        // if it's a string we bail out early
        if (typeof node === "string") {
            return node;
        }

        const children = node.props?.children ? toChildArray(node.props.children).map(c => this.transformTableElements(c, record)) : null;

        // add our props to fields
        if (node.type === FieldComponent) {
            return cloneElement(node, { ...node.props, record }, children);
        }

        // transform some tags
        const tagMap = {
            "headCell": "th",
            "cell": "td",
            "row": "tr",
        };
        if (node.type in tagMap) {
            // transform tag according to the map
            return createElement(tagMap[node.type] , {}, children);
        } else {
            // just add the transformed children
            return cloneElement(node, node.props, children);
        }
    }
}

class FieldComponent extends Component {
	render(props, state) {
		return createElement("span", null, "field(name=", props.name, ", value=", props.record[props.name], ")", props.children);
	}
}

function xmlToPreact(node) {
    if (node.nodeType === Node.ELEMENT_NODE) {
        let eltype = node.tagName;

        // attributes
        const attrs = {};
        for (let attr of node.attributes) {
            attrs[attr.name] = attr.value;
        }

        // special types
        if (eltype == "field") {
            eltype = FieldComponent;
        }

        // children
        const children = [];
        node.childNodes.forEach(child => {
            const result = xmlToPreact(child);
            if (result != null) {
                children.push(result);
            }
        });

        return createElement(eltype, attrs, ...children);
    }

    if (node.nodeType === Node.TEXT_NODE) {
        return node.textContent;
    }

    return null;
}

function saneXpath(xmldoc, xpath) {
    const results = [];
    let it = xmldoc.evaluate(xpath, xmldoc);
    let node = it.iterateNext();
    while (node) {
        results.push(node);
        node = it.iterateNext();
    }
    if (results.length == 0) {
        return null;
    }
    return results
}

function viewDefinitionToPreact(definition) {
    const elements = [];
    for (const child of definition.childNodes) {
        const preact = xmlToPreact(child);
        if (preact != null) {
            elements.push(preact);
        }
    };
    return createElement(ListViewComponent, {model: view.model_name}, ...elements);
}

const view_type = saneXpath(doc, "/view")[0].getAttribute("type");
console.log(view_type);
render(
    viewDefinitionToPreact(saneXpath(doc, "/view/definition")[0]),
    document.body,
);
