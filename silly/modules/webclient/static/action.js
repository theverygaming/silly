import { Bus } from "@bus";

export const actionBus = new Bus();

export class Action {
    constructor({ view, recordset }) {
        this.view = view;
        this.recordset = recordset;
    }
}
