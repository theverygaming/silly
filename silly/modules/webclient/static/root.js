import { createElement, cloneElement, render, Component, toChildArray, Fragment } from "@preact";
import { env } from "@orm";
import { getView } from "@views/view";
import { ErrorHandler } from "@error";

import "@views/listView"; // gotta import so the code runs.. // FIXME!!

let view = await (await env.model("view").call("search", [[]], {limit: 1})).call("webclient_read", [["model_name", "xml"]]);
console.log(view);
console.log(view.xml);


class App extends Component {
    async componentDidMount() {
        const recordset = await (await env.model("xmlid").call("search", [[]], {})).call("webclient_read", [["id", "xmlid", "model_name", "model_id", "source_module"]]);
        this.setState({ recordset });
    }

    render() {
        let extraEl = null;
        if (this.state.recordset) {
            extraEl = getView(view.xml, this.state.recordset);
        }
        return createElement(ErrorHandler, {}, extraEl);
    }
}

render(
    createElement(App, {}),
    document.body,
);
