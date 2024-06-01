import { jsonrpc } from "@jsonrpc";

export class ViewHelper {
    #model;

    constructor(model) {
        this.#model = model;
    }

    async searchRecords(fields, domain = []) {
        return jsonrpc("/webclient/jsonrpc", "search_read", 0, {
            model: this.#model,
            domain: domain,
            fields: [...new Set([...fields, "id"])],
        });
    }

    async browseRecords(fields, ids) {
        return jsonrpc("/webclient/jsonrpc", "browse_read", 0, {
            model: this.#model,
            ids: ids,
            fields: [...new Set([...fields, "id"])],
        });
    }

    async writeRecords(data, ids) {
        return jsonrpc("/webclient/jsonrpc", "browse_write", 0, {
            model: this.#model,
            ids: ids,
            data: data,
        });
    }
}
