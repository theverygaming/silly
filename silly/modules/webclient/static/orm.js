import { jsonrpc } from "@tools/jsonrpc";

function jsonrpc_id() {
    return Math.floor(Math.random() * 0xFFFFFFFF);
}

function convORMJsonrpcType(env, obj) {
    const isSillyRecordset = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyRecordset" && typeof obj.model === "string" && Array.isArray(obj.records);
    const isSillyFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyFieldValue" && typeof obj.type === "string";
    // TODO: actually convert field value types!
    if (isSillyFieldValue(obj)) {
        const vals = obj;
        vals.value = convORMJsonrpcType(env, vals.value);
        return vals;
    }
    if (isSillyRecordset(obj)) {
        const fields = [];
        // accumulate ids and field values for the recordset, recurse into all field values and convert them
        for (const rec of obj.records) {
            const fields_obj = {};
            for (const [key, value] of Object.entries(rec)) {
                fields_obj[key] = convORMJsonrpcType(env, value);
            }
            fields.push(fields_obj);
        }
        return new Recordset(env, obj.model, fields).asProxy();
    }
    return obj;
}

class Recordset {
    constructor(env, model, fields) {
        this.env = env;
        this.model = model;
        this.fields = fields;
    }

    // Recordset methods

    ensureOne() {
        if (this.fields.length != 1) {
            throw new Error(`ensureOne found ${this.fields.length} IDs in recordset`);
        }
    }

    get id() {
        return this.getFieldValue("id");
    }

    get ids() {
        return this.getFieldValueMulti("id");
    }

    getField(name) {
        this.ensureOne();
        return this.fields[0][name];
    }

    getFieldMulti(name) {
        return this.fields.map(f => f[name]);
    }

    getFieldValue(name) {
        return this.getField(name).value;
    }

    getFieldValueMulti(name) {
        return this.getFieldMulti(name).map(f => f.value);
    }

    asProxy() {
        return new Proxy(this, {
            get(target, prop, receiver) {
                if (!(prop in target) &&target.ids.length == 1 && prop in target.fields[0]) {
                    return target.getFieldValue(prop);
                }
                return Reflect.get(...arguments);
            },
        });
    }

    getRecordAtIdx(idx) {
        if (idx >= this.fields.length) {
            throw new Error(`cannot get record at index ${idx}, there are only ${this.fields.length} records in this recordset`);
        }
        return new Recordset(this.env, this.model, [this.fields[idx]]).asProxy();
    }

    getNRecords() {
        return this.fields.length;
    }

    [Symbol.iterator]() {
        let idx = 0;
        const ids = this.ids;

        return {
            next: () => {
                if (idx < ids.length) {
                    return { value: this.getRecordAtIdx(idx++), done: false };
                } else {
                    return { done: true };
                }
            }
        };
    }

    // Core RPC methods

    async call(method, args = [], kwargs = {}) {
        const params = {
            model: this.model,
            fn: method,
            args: args,
            kwargs: kwargs,
        };
        const has_records = this.fields.length > 0;
        if (has_records) {
            params.ids = this.ids;
        }
        let ret = await jsonrpc(this.env.url, has_records ? "env_exec_ids" : "env_exec", jsonrpc_id(), params);
        ret = convORMJsonrpcType(this.env, ret);
        return ret;
    }

    // Syntax sugar RPC methods
}

class Environment {
    constructor(url) {
        this.url = url;
    }

    model(name) {
        return new Recordset(this, name, []);
    }

    async lookupXMLId(xmlid, model = null) {
        return await this.model("core.xmlid").call("lookup", [xmlid], {...(model && {model: model})})
    }
}

export const env = new Environment(window.location.origin + "/api/jsonrpc");
