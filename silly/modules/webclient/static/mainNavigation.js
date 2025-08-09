import { Component } from "@preact";
import { xml2preact } from "@tools/xml2preact";
import { actionBus, Action } from "@action";
import { getView } from "@views/view";
import { env } from "@orm";
import { loadingNotifPromise } from "@appBus";

export class MainNavigation extends Component {
    state = {
        gridMenu: true,
        navHistory: [],
        navHistoryActiveIdx: -1,
        menubar: [
            {name: "test1", url: "#test1"},
            {name: "test2", url: "#test2"},
            {
                name: "more",
                children: [
                    {name: "test3", url: "#test3"},
                    {name: "test4", url: "#test4"},
                    {name: "test5", url: "#test5"},
                ],
            },
        ]
    };

    async componentDidMount() {
        actionBus.subscribe(async (act) => {
            console.log(act);
            let view = await loadingNotifPromise("View", (await env.lookupXMLId(act.view, "webclient.view")).call("webclient_read", [["model_name", "xml"]]));
            console.log(view);
            console.log(view.xml);
            this.setState({
                navHistory: [...this.state.navHistory.slice(0, this.state.navHistoryActiveIdx+1), {
                    name: "idk",
                    xml: view.xml,
                    recordset: act.recordset,
                }],
                navHistoryActiveIdx: this.state.navHistoryActiveIdx + 1
            });
        });
    }

    render() {
        return xml2preact(`
<template>
    <nav class="navbar" role="navigation" aria-label="main navigation">
        <div class="navbar-brand">
            <button class="navbar-item" t-att-onClick="toggleGridMenu">
                <i class="bi bi-grid"/>
            </button>
        </div>
        <div class="navbar-menu">
            <div t-if="!state.gridMenu" class="navbar-start">
                <t t-foreach="state.menubar" t-as="item">
                    <a t-if="!('children' in item)" class="navbar-item" t-att-href="item.url" t-out="item.name"/>
                    <div t-if="'children' in item" class="navbar-item has-dropdown is-hoverable">
                        <a class="navbar-link" t-out="item.name"/>
                        <div class="navbar-dropdown">
                            <t t-foreach="item.children" t-as="child">
                                <a class="navbar-item" t-att-href="child.url" t-out="child.name"/>
                            </t>
                        </div>
                    </div>
                </t>
            </div>
            <div class="navbar-end">
                <div class="navbar-item">
                    <button class="button is-primary" t-att-onClick="meowButton">
                        meow
                    </button>
                </div>
            </div>
        </div>
    </nav>
    <nav class="breadcrumb">
        <ul>
            <t t-set="idx" t-value="0"/>
            <t t-foreach="state.navHistory" t-as="item">
                <li t-att-class="idx == state.navHistoryActiveIdx ? 'is-active' : null"><a t-att-onClick="breadcrumbClick" t-att-data-idx="idx"><t t-out="item.name"/></a></li>
                <t t-set="idx" t-value="idx + 1"/>
            </t>
        </ul>
    </nav>
    <div>
        <!--
            To preserve component state we hide them. This is cursed but otherwise
            I got stupid errors when preact rendered components
            that were missing their old references

            It's past midnight and I don't want to deal with this shit
        -->
        <t t-set="idx" t-value="0"/>
        <t t-foreach="state.navHistory" t-as="item">
            <div t-att-style="idx == state.navHistoryActiveIdx &amp;&amp; !state.gridMenu ? null : 'display: none;'">
                <t t-out="getView(item.xml, item.recordset)"/>
            </div>
            <t t-set="idx" t-value="idx + 1"/>
        </t>
    </div>
    <t t-if="state.gridMenu">
        <button class="button is-primary" t-att-onClick="testThingyButton">
            test thingy
        </button>
    </t>
</template>`,
            {
                props: this.props,
                state: this.state,
                getView: getView,
                toggleGridMenu: ((x) => { this.setState({gridMenu: !this.state.gridMenu}); }),
                breadcrumbClick: (e) => {
                    this.setState({navHistoryActiveIdx: parseInt(e.target.dataset.idx)});
                },
                testThingyButton: () => {
                    (async () => {
                        return await loadingNotifPromise("Model Data", (await env.model("core.xmlid").call("webclient_search", [[]], {})).call("webclient_read", [["id", "xmlid", "model_name", "model_id", "source_module"]]));
                    })().then((rec) => {
                        actionBus.publish(new Action({view: "webclient.view_1", recordset: rec}));
                        this.setState({gridMenu: false});
                    });
                },
                meowButton: () => {
                    console.log("meow");
                    const urls = [
                        "https://upload.wikimedia.org/wikipedia/commons/7/74/2015-11-24.%CE%BD%CE%B9%CE%B1%CE%BF%CF%8D%CF%81%CE%B9%CF%83%CE%BC%CE%B1.%CE%9D%CE%B9%CE%AC%CE%BF%CF%85.noise_reduced.flac",
                        "https://upload.wikimedia.org/wikipedia/commons/3/31/Felis_silvestris_catus.ogg",
                        "https://upload.wikimedia.org/wikipedia/commons/0/0c/Meow_domestic_cat.ogg",
                        "https://upload.wikimedia.org/wikipedia/commons/6/62/Meow.ogg",
                    ];
                    new Audio(urls[Math.floor(Math.random() * urls.length)]).play();
                },
            },
        );
    }
}
