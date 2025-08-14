import { Component } from "@preact";
import { xml2preact } from "@tools/xml2preact";

export class FieldComponent extends Component {
    render(props, state) {
        const attrProps = Object.fromEntries(
            Object.entries(props).filter(([key]) => 
                !["name", "record", "children", "label", "editable"].includes(key)
            )
        );

        if (!("id" in attrProps)) {
            attrProps["id"] = props.name;
        }

        return xml2preact(`
<template>
    <label t-if="props.label" t-att-for="attrProps.id" t-out="props.label"/>
    <span t-if="!props.editable" t-attrs="attrProps">field(name=<t t-out="props.name"/>, value=<t t-out="props.record[props.name]"/>)</span>
    <input t-if="props.editable" t-attrs="attrProps" t-att-value="props.record[props.name]" t-att-onInput="onInput"> </input>
</template>
            `,
            {
                props,
                attrProps,
                onInput: (ev) => {
                    const value = ev.target.value;
                    props.record.setField(props.name, value);
                    props.record.save();
                },
            },
        );
    }
}
