import { Component } from "@preact";
import { xml2preact, safeIshEval } from "@tools/xml2preact";
import { actionBus, Action } from "@action";
import { getView } from "@views/view";
import { env } from "@orm";
import { loadingNotifPromise, loadingNotifAsync } from "@appBus";

export class MainNavigation extends Component {
    state = {
        gridMenu: true,
        navHistory: [],
        navHistoryActiveIdx: -1,
        menubar: [],
        mainMenuItems: [],
    };

    async componentDidMount() {
        actionBus.subscribe(async (act) => {
            console.log(act);
            let [view, recordset] = await loadingNotifPromise("View, Recordset", (async () => {
                let v = null;
                if (act.view_xmlid) {
                    v = await env.lookupXMLId(act.view_xmlid, "webclient.view");
                } else {
                    v = await env.model("webclient.view").call("browse", [act.view_id]);
                }
                let vd =  await v.call("webclient_read", [["model_name", "xml"]]);
                let rs = act.recordset;
                if (!rs) {
                    rs = await (await env.model(vd.model_name).call("webclient_search", [safeIshEval(act.domain)], {})).call("webclient_read", [["id", "xmlid", "model_name", "model_id", "source_module"]]);
                }
                return [vd, rs];
            })());
            console.log(view);
            console.log(view.xml);
            this.setState({
                navHistory: [...this.state.navHistory.slice(0, this.state.navHistoryActiveIdx+1), {
                    name: "idk",
                    xml: view.xml,
                    recordset: recordset,
                }],
                navHistoryActiveIdx: this.state.navHistoryActiveIdx + 1
            });
        });

        loadingNotifPromise("Main Menu", env.model("webclient.menuitem").call("get_main_menu_dict")).then(
            (items) => {
                this.setState({mainMenuItems: items});
            }
        );
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
                <t t-set="idx" t-value="0"/>
                <t t-foreach="state.menubar" t-as="item">
                    <a t-if="!('children' in item)" class="navbar-item" t-att-onClick="menubarClick" t-att-data-idx="idx" t-out="item.name"/>
                    <div t-if="'children' in item" class="navbar-item has-dropdown is-hoverable">
                        <a class="navbar-link" t-out="item.name"/>
                        <div class="navbar-dropdown">
                            <t t-set="idxb" t-value="0"/>
                            <t t-foreach="item.children" t-as="child">
                                <a class="navbar-item" t-att-onClick="menubarClick" t-att-data-idx="idx" t-att-data-idxb="idxb" t-out="child.name"/>
                                <t t-set="idxb" t-value="idxb + 1"/>
                            </t>
                        </div>
                    </div>
                    <t t-set="idx" t-value="idx + 1"/>
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
    <nav class="breadcrumb" t-if="!state.gridMenu">
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
        <t t-set="idx" t-value="0"/>
        <t t-foreach="state.mainMenuItems" t-as="item">
            <button class="button is-primary" t-att-onClick="mainMenuClick" t-att-data-idx="idx" t-out="item.name"/>
            <t t-set="idx" t-value="idx + 1"/>
        </t>
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
                mainMenuClick: (e) => {
                    const menuitem = this.state.mainMenuItems[parseInt(e.target.dataset.idx)];
                    if (!menuitem.action) {
                        return;
                    }
                    actionBus.publish(new Action({view_id: menuitem.action.view_id, domain: menuitem.action.domain}));
                    loadingNotifAsync("Submenu", async () => {
                        return (await env.model("webclient.menuitem").call("browse", [menuitem.id])).call("get_submenus_dict");
                    }).then(
                        (items) => {
                            this.setState({menubar: items});
                        }
                    );
                    this.setState({gridMenu: false});
                },
                menubarClick: (e) => {
                    const menuitem = e.target.dataset.idxb ? this.state.menubar[parseInt(e.target.dataset.idx)].children[parseInt(e.target.dataset.idxb)] : this.state.menubar[parseInt(e.target.dataset.idx)];
                    if (!menuitem.action) {
                        return;
                    }
                    actionBus.publish(new Action({view_id: menuitem.action.view_id, domain: menuitem.action.domain}));
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
