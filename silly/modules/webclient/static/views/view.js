import { createElement, cloneElement, Component, toChildArray } from "@preact";
import { registry } from "@registry";
import { FieldComponent } from "@views/field";
import { saneXpath } from "@tools/xml";


export class View extends Component {
    
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

function viewDefinitionToPreact(component, definition, recordset) {
    const elements = [];
    for (const child of definition.childNodes) {
        const preact = xmlToPreact(child);
        if (preact != null) {
            elements.push(preact);
        }
    };
    return createElement(component, {recordset}, ...elements);
}

export function getView(xml, recordset) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, "application/xml");
    if (doc.querySelector("parsererror")) {
        throw new Error("error while parsing XML");
    }
    const component = registry.get("viewComponents").get(saneXpath(doc, "/view")[0].getAttribute("component"));
    return viewDefinitionToPreact(component, saneXpath(doc, "/view/definition")[0], recordset);
}
