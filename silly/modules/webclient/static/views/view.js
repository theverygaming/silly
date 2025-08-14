import { createElement, cloneElement, Component, toChildArray } from "@preact";
import { registry } from "@registry";
import { FieldComponent } from "@views/field";
import { saneXpath } from "@tools/xml";


export class View extends Component {
    transformElements(node, tagMap, record, extraPropsFn = null) {
        if (!node) {
            return null;
        }

        // if it's a string we bail out early
        if (typeof node === "string") {
            return node;
        }

        let extraProps = extraPropsFn?.(node) || {};

        const children = node.props?.children ? toChildArray(node.props.children).map(c => this.transformElements(c, tagMap, record, extraPropsFn)) : null;

        // add our props to fields
        if (node.type === FieldComponent) {
            return cloneElement(node, { ...extraProps, ...node.props, record }, children);
        }

        // transform some tags
        if (node.type in tagMap) {
            // transform tag according to the map
            return createElement(tagMap[node.type] , { ...extraProps }, children);
        } else {
            // just add the transformed children
            return cloneElement(node, {...extraProps, ...node.props}, children);
        }
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
