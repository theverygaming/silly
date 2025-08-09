import { createElement, cloneElement, render, Component, toChildArray, Fragment } from "@preact";
import { env } from "@orm";
import { getView } from "@views/view";
import { ErrorHandler } from "@error";
import { MainNavigation } from "@mainNavigation";
import { LoadingOverlay } from "@loadingOverlay";
import { xml2preact } from "@tools/xml2preact";

import "@views/listView"; // gotta import so the code runs.. // FIXME!!
import "@views/formView"; // gotta import so the code runs.. // FIXME!!

let view = (await (await env.model("webclient.view").call("webclient_search", [[]], {limit: 2})).call("webclient_read", [["model_name", "xml"]])).getRecordAtIdx(1);
console.log(view);
console.log(view.xml);


class App extends Component {
    render() {
        return xml2preact(`
<template>
    <t t-component="ErrorHandler">
        <t t-component="LoadingOverlay"/>
        <t t-component="MainNavigation"/>
    </t>
</template>
            `,
            {
                ErrorHandler,
                MainNavigation,
                LoadingOverlay,
            },
        );
    }
}

render(
    createElement(App, {}),
    document.body,
);
