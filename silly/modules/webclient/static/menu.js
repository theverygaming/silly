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
                    <button class="button is-primary" t-att-onClick="meowButton">
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
