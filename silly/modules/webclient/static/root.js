import { createElement, cloneElement, render, Component, toChildArray, Fragment } from "@preact";
import { env } from "@orm";
import { getView } from "@views/view";
import { ErrorHandler } from "@error";
import { MainNavigation } from "@mainNavigation";
import { xml2preact } from "@tools/xml2preact";

import "@views/listView"; // gotta import so the code runs.. // FIXME!!
import "@views/formView"; // gotta import so the code runs.. // FIXME!!

let view = (await (await env.model("webclient.view").call("webclient_search", [[]], {limit: 2})).call("webclient_read", [["model_name", "xml"]])).getRecordAtIdx(1);
console.log(view);
console.log(view.xml);


class App extends Component {
    async componentDidMount() {
        const recordset = await (await env.model("xmlid").call("webclient_search", [[]], {})).call("webclient_read", [["id", "xmlid", "model_name", "model_id", "source_module"]]);
        this.setState({ recordset });
    }

    render() {
        let extraEl = null;
        if (this.state.recordset) {
            extraEl = getView(view.xml, this.state.recordset);
        }
        return xml2preact(`
<template>
    <t t-component="ErrorHandler">
        <t t-component="MainNavigation">
            <t t-out="extraEl"/>
        </t>
    </t>
</template>
            `,
            {
                ErrorHandler,
                extraEl,
                MainNavigation,
            },
        );
    }
}

render(
    createElement(App, {}),
    document.body,
);
