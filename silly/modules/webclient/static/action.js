import { Bus } from "@bus";

export const actionBus = new Bus();

export class Action {
    constructor({view_xmlid=null, view_id=null, recordset=null, domain=null}) {
        this.view_xmlid = view_xmlid;
        this.view_id = view_id;
        this.recordset = recordset;
        this.domain = domain;
    }
}
