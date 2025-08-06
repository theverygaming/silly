import { createElement, Fragment } from "@preact";
import { saneXpath } from "@tools/xml";

function safeIshEval(expr, ctx = {}) {
    const keys = Object.keys(ctx);
    const values = Object.values(ctx);
    const code = `return (${expr});`;
    return new Function(...keys, code)(...values);
}

function xmlToPreact(node, ctx = {}) {
    function render_children(c_node, c_ctx) {
        const children = [];
        c_node.childNodes.forEach(child => {
            const result = xmlToPreact(child, c_ctx);
            if (result != null) {
                children.push(result);
            }
        });
        return children;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
        let eltype = node.tagName;
        
        let special_state = null;
        let special_state_var = null;

        // attributes
        const out_attrs = {};
        for (const attr of node.attributes) {
            // t-att
            if (attr.name.startsWith("t-att-")) {
                const val = safeIshEval(attr.value, ctx);
                if (val != undefined && val != null) {
                    out_attrs[attr.name.slice("t-att-".length)] = val;
                }
                continue;
            }
            // t-if
            if (attr.name == "t-if") {
                if(!safeIshEval(attr.value, ctx)) {
                    return null;
                }
                continue
            }
            // t-foreach / t-as
            if (attr.name == "t-foreach") {
                const iterable = safeIshEval(attr.value, ctx);
                const as = node.attributes.getNamedItem("t-as");
                special_state = "foreach";
                special_state_var = {
                    "iter": iterable,
                };
                if (as) {
                    special_state_var["iter_var"] = as.value;
                }
                continue
            }
            if (attr.name == "t-as") {
                continue
            }
            // t-out
            if (attr.name == "t-out") {
                special_state = "out";
                special_state_var = safeIshEval(attr.value, ctx);
                continue
            }
            // t-component
            if (attr.name == "t-component") {
                special_state = "component";
                special_state_var = safeIshEval(attr.value, ctx);
                continue
            }
            // t-set / t-value
            if (attr.name == "t-set") {
                const set_var = attr.value;
                const code = node.attributes.getNamedItem("t-value");
                if (!code) {
                    throw new Error("t-set specified without t-value attribute set");
                }
                const value = safeIshEval(code.value, ctx);
                ctx[set_var] = value;
                continue
            }
            if (attr.name == "t-value") {
                continue
            }
            // default attribute
            out_attrs[attr.name] = attr.value;
        }

        // special types
        if (eltype == "t") {
            eltype = Fragment;
        }

        switch(special_state) {
            case "foreach": {
                const elements = [];
                for (const item of special_state_var["iter"]) {
                    if ("iter_var" in special_state_var) {
                        ctx[special_state_var["iter_var"]] = item;
                    }
                    elements.push(createElement(eltype, out_attrs, ...render_children(node, ctx)));
                }
                return createElement(Fragment, null, ...elements);
            }
            case "out": {
                return createElement(eltype, out_attrs, special_state_var);
            }
            case "component": {
                eltype = special_state_var;
                break;
            }
        }

        return createElement(eltype, out_attrs, ...render_children(node, ctx));
    }

    if (node.nodeType === Node.TEXT_NODE) {
        return node.textContent;
    }

    return null;
}

export function xml2preact(xml, ctx = {}) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, "application/xml");
    if (doc.querySelector("parsererror")) {
        throw new Error("error while parsing XML");
    }
    const template = saneXpath(doc, "/template")[0];
    const elements = [];
    for (const child of template.childNodes) {
        const preact = xmlToPreact(child, ctx);
        if (preact != null) {
            elements.push(preact);
        }
    };
    return createElement(Fragment, null, ...elements);
}
