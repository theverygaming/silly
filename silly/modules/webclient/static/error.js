import { createElement, Component } from "@preact";
import { xml2preact } from "@tools/xml2preact";


export class ErrorHandler extends Component {
    state = {
        error: null,
        trace: null,
    };

    static getDerivedStateFromError(error) {
        console.error(error);
        return {
            error: error.message,
            trace: error.stack,
        };
    }

    render() {
        return xml2preact(`
<template>
    <div t-if="state.error" class="modal is-active">
        <div class="modal-background"/>
        <div class="modal-content">
            <div class="box">
                <p class="title">Error!</p>
                <p class="subtitle" t-out="state.error"/>
                <div>
                    <code t-out="state.trace"/>
                </div>
                <button class="button" t-att-onClick="onClickClose">Close</button>
            </div>
        </div>
    </div>
    <t t-out="props.children"/>
</template>`,
            {
                props: this.props,
                state: this.state,
                onClickClose: (() => { this.setState({error: null, trace: null}); }),
            },
        );
    }
}
