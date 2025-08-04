import { Component } from "@preact";
import { xml2preact } from "@tools/xml2preact";

export class Menu extends Component {
    state = {
        gridMenu: false,
    };

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
                <t t-foreach="navs" t-as="item">
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
                    <button class="button is-primary">
                        meow
                    </button>
                </div>
            </div>
        </div>
    </nav>
    <t t-if="!state.gridMenu" t-out="props.children"/>
</template>`,
            {
                props: this.props,
                state: this.state,
                toggleGridMenu: ((x) => { this.setState({gridMenu: !this.state.gridMenu}); }),
                navs: [
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
                ],
            },
        );
    }
}
