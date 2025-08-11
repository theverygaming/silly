import { createElement, render, Component } from "@preact";
import { ErrorHandler } from "@error";
import { MainNavigation } from "@mainNavigation";
import { LoadingOverlay } from "@loadingOverlay";
import { xml2preact } from "@tools/xml2preact";

import "@views/listView"; // gotta import so the code runs.. // FIXME!!
import "@views/formView"; // gotta import so the code runs.. // FIXME!!

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
