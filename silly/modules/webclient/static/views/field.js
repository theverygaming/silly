import { createElement, Component } from "@preact";

export class FieldComponent extends Component {
    render(props, state) {
        const attrProps = Object.fromEntries(
            Object.entries(props).filter(([key]) => 
                key !== "name" && key !== "record" && key !== "children"
            )
        );

        return createElement("span", attrProps, "field(name=", props.name, ", value=", props.record[props.name], ")", props.children);
    }
}
