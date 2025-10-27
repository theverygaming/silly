import { createElement, toChildArray } from "@preact";
import { View } from "@views/view";
import { registry } from "@registry";
import { actionBus, Action } from "@action";


export class ListView extends View {
    state = {};

    onRowClick(e) {
        // TODO: work with index in recordset or smth instead maybe probably or idk
        // (thinking of paging that's prolly also bad so should work by ID..)
        // fix it at least!
        const recidx = parseInt(e.target.closest("tr").dataset.recidx);
        actionBus.publish(new Action({view_xmlid: "webclient.view_2", recordset: this.props.recordset.getRecordAtIdx(recidx)}));
        if (recidx == 1) {
            throw new Error("test: record with Index 1 clicked");
        }
    }

    render(props, state) {
        const tagMap = {
            "headCell": "th",
            "cell": "td",
            "row": "tr",
        };

        const onRowClick = (e) => {
            this.onRowClick(e);
        };

        let headNode = toChildArray(props.children).find(child => child.type === "head");
        let rowNode = toChildArray(props.children).find(child => child.type === "row");

        // table head
        let thead = createElement("thead", {}, createElement("tr", { }, toChildArray(headNode.props.children).map(child => {
            return this.transformElements(child, tagMap, {}, {});
        })));

        // rows
        const rowTemplate = rowNode;
        const rows = Array.from(props.recordset).map((record, idx) => {
            return this.transformElements(rowTemplate, tagMap, {record}, {}, (node) => {
                if (node.type == "row") {
                    return {
                        onClick: onRowClick,
                        "data-recidx": idx,
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
}

registry.get("viewComponents").add("ListView", ListView);
