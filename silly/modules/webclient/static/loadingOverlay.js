import { Component } from "@preact";
import { xml2preact } from "@tools/xml2preact";
import { appBus, MESSAGE_TYPES } from "@appBus";

export class LoadingOverlay extends Component {
    state = {
        loadingStack: [],
    };

    async componentDidMount() {
        appBus.subscribe(async (msg) => {
            if (msg.type == MESSAGE_TYPES.LOADING) {
                this.setState((prev) => {
                    const stack = [...prev.loadingStack];

                    if (msg.data.state) {
                        stack.push(msg.data.msg);
                    } else {
                        // remove first match
                        const idx = stack.indexOf(msg.data.msg);
                        if (idx != -1) {
                            stack.splice(idx, 1);
                        }
                    }

                    console.log(stack);

                    return { loadingStack: stack };
                });
            }
        });
    }

    render() {
        return xml2preact(`
<template>
    <div t-if="state.loadingStack.length" class="modal is-active">
        <div class="modal-background"/>
        <div class="modal-content">
            <span class="loader"/>
            <t t-foreach="state.loadingStack" t-as="msg">
                <p t-out="msg"/>
            </t>
        </div>
    </div>
</template>`,
            {
                props: this.props,
                state: this.state,
            },
        );
    }
}
