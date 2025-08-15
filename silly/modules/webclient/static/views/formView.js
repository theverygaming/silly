import { createElement, toChildArray, Fragment } from "@preact";
import { View } from "@views/view";
import { registry } from "@registry";

export class FormView extends View {
    state = {};

    render(props, state) {
        const tagMap = {
            "form": Fragment,
        };
        let headNode = toChildArray(props.children).find(child => child.type === "head");
        let formNode = toChildArray(props.children).find(child => child.type === "form");

        // head
        let head = createElement("div", {}, toChildArray(headNode.props.children).map(child => {
            return this.transformElements(child, tagMap, {}, {});
        }));

        // stuff
        const record = props.recordset.getRecordAtIdx(0);
        const body = this.transformElements(formNode, tagMap, {record}, {});
        return createElement("div", {},
            head,
            createElement("div", {}, body),
        );
    }
}

registry.get("viewComponents").add("FormView", FormView);
