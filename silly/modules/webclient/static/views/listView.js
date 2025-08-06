import { createElement, cloneElement, toChildArray } from "@preact";
import { View } from "@views/view";
import { registry } from "@registry";
import { FieldComponent } from "@views/field";
import { actionBus, Action } from "@action";


export class ListView extends View {
    state = {};

    onRowClick(e) {
        // TODO: work with index in recordset or smth instead maybe probably or idk
        // fix it at least!
        const recid = parseInt(e.target.closest("tr").dataset.recid);
        console.log(recid);
        actionBus.publish(new Action({view: "webclient.view_2", recordset: this.props.recordset.getRecordAtIdx(recid-1)}));
        if (recid == 1) {
            throw new Error("test: record with ID 1 clicked");
        }
    }

    render(props, state) {
        const onRowClick = (e) => {
            this.onRowClick(e);
        };

        let headNode = toChildArray(props.children).find(child => child.type === "head");
        let rowNode = toChildArray(props.children).find(child => child.type === "row");

        // table head
        let thead = createElement("thead", {}, createElement("tr", { }, toChildArray(headNode.props.children).map(child => {
            return this.transformTableElements(child, null);
        })));

        // rows
        const rowTemplate = rowNode;
        const rows = Array.from(props.recordset).map(record => {
            return this.transformTableElements(rowTemplate, record, (node) => {
                if (node.type == "row") {
                    return {
                        onClick: onRowClick,
                        "data-recid": record.id,
                    };
                }
                return null;
            });
        });
        return createElement("table", { class: "table" },
            thead,
            createElement("tbody", {}, rows),
        );
    }

    transformTableElements(node, record, extraPropsFn = null) {
        if (!node) {
            return null;
        }

        // if it's a string we bail out early
        if (typeof node === "string") {
            return node;
        }

        let extraProps = extraPropsFn?.(node) || {};

        const children = node.props?.children ? toChildArray(node.props.children).map(c => this.transformTableElements(c, record, extraPropsFn)) : null;

        // add our props to fields
        if (node.type === FieldComponent) {
            return cloneElement(node, { ...extraProps, ...node.props, record }, children);
        }

        // transform some tags
        const tagMap = {
            "headCell": "th",
            "cell": "td",
            "row": "tr",
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

registry.get("viewComponents").add("ListView", ListView);
