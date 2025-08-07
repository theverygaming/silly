import { createElement, cloneElement, toChildArray, Fragment } from "@preact";
import { View } from "@views/view";
import { registry } from "@registry";
import { FieldComponent } from "@views/field";


export class FormView extends View {
    state = {};

    render(props, state) {
        let headNode = toChildArray(props.children).find(child => child.type === "head");
        let formNode = toChildArray(props.children).find(child => child.type === "form");

        // head
        let head = createElement("div", {}, toChildArray(headNode.props.children).map(child => {
            return this.transformElements(child, null);
        }));

        // stuff
        const record = props.recordset.getRecordAtIdx(0);
        const body = this.transformElements(formNode, record);
        return createElement("div", {},
            head,
            createElement("div", {}, body),
        );
    }

    // FIXME: this function is partly duplicated in listView, it should be abstracted and put into the base view class!
    transformElements(node, record, extraPropsFn = null) {
        if (!node) {
            return null;
        }

        // if it's a string we bail out early
        if (typeof node === "string") {
            return node;
        }

        let extraProps = extraPropsFn?.(node) || {};

        const children = node.props?.children ? toChildArray(node.props.children).map(c => this.transformElements(c, record, extraPropsFn)) : null;

        // add our props to fields
        if (node.type === FieldComponent) {
            return cloneElement(node, { ...extraProps, ...node.props, record }, children);
        }

        // transform some tags
        const tagMap = {
            "form": Fragment,
        };
        if (node.type in tagMap) {
            // transform tag according to the map
            return createElement(tagMap[node.type] , { ...extraProps }, children);
        } else {
            // just add the transformed children
            return cloneElement(node, {...extraProps, ...node.props}, children);
        }
    }
}

registry.get("viewComponents").add("FormView", FormView);
