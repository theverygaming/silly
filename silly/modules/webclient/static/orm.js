import { jsonrpc } from "@tools/jsonrpc";

function jsonrpc_id() {
    return Math.floor(Math.random() * 0xFFFFFFFF);
}

function convORMJsonrpcType(env, obj) {
    const isSillyRecordset = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyRecordset" && typeof obj.model === "string" && Array.isArray(obj.records) && typeof obj.spec === "object";
    const isSillyIntFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyIntFieldValue" && typeof obj.type === "string";
    // TODO: actually convert field value types!
    if (isSillyIntFieldValue(obj)) {
        const vals = obj;
        return convORMJsonrpcType(env, vals.value);
    }
    if (isSillyRecordset(obj)) {
        const isSillyFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyFieldValue";
        const fields = [];
        // accumulate ids and field values for the recordset, recurse into all field values and convert them
        for (const rec of obj.records) {
            const fields_obj = {};
            for (let [key, value] of Object.entries(rec)) {
                if (isSillyFieldValue(value)) {
                    value.objtype = "sillyIntFieldValue";
                    value.type = obj.spec.field_info[key].type;
                    value.rel_model = obj.spec.field_info[key].rel_model;
                }
                fields_obj[key] = convORMJsonrpcType(env, value);
            }
            fields.push(fields_obj);
        }
        return new Recordset(env, obj.model, obj.spec, fields).asProxy();
    }
    return obj;
}

class Recordset {
    constructor(env, model, modelSpec, fields) {
        this.env = env;
        this.model = model;
        this.modelSpec = modelSpec;
        this._fields = fields;
    }

    // Recordset methods

    _ensureIsRWAble() {
        if (!this.modelSpec) {
            throw new Error(`_ensureIsRWAble: missing model spec`);
        }
    }

    ensureOne() {
        if (this.getNRecords() != 1) {
            throw new Error(`ensureOne found ${this.getNRecords()} IDs in recordset`);
        }
    }

    getField(name) {
        this.ensureOne();
        if (this.getNRecords()) {
            this._ensureIsRWAble();
        }
        return this.getFieldMulti(name)[0];
    }

    getFieldMulti(name) {
        if (this.getNRecords()) {
            this._ensureIsRWAble();
        }
        return this._fields.map(f => f[name]);
    }

    getFieldSpec(name) {
        this._ensureIsRWAble();
        return this.modelSpec.field_info[name];
    }

    asProxy() {
        return new Proxy(this, {
            get(target, prop, receiver) {
                if (!(prop in target) && target.getNRecords() == 1 && prop in target._fields[0]) {
                    return target.getField(prop);
                }
                return Reflect.get(...arguments);
            },
        });
    }

    getRecordAtIdx(idx) {
        if (idx >= this.getNRecords()) {
            throw new Error(`cannot get record at index ${idx}, there are only ${this.getNRecords()} records in this recordset`);
        }
        return new Recordset(this.env, this.model, this.modelSpec, [this._fields[idx]]).asProxy();
    }

    getNRecords() {
        return this._fields.length;
    }

    [Symbol.iterator]() {
        let idx = 0;

        return {
            next: () => {
                if (idx < this.getNRecords()) {
                    return { value: this.getRecordAtIdx(idx++), done: false };
                } else {
                    return { done: true };
                }
            }
        };
    }

    // Core RPC methods

    async call(method, args = [], kwargs = {}, conv = true) {
        const params = {
            model: this.model,
            fn: method,
            args: args,
            kwargs: kwargs,
        };
        const has_records = this.getNRecords() > 0;
        if (has_records) {
            params.ids = this.getFieldMulti("id");
        }
        let ret = await jsonrpc(this.env.url, has_records ? "env_exec_ids" : "env_exec", jsonrpc_id(), params);
        if (conv) {
            ret = convORMJsonrpcType(this.env, ret);
        }
        return ret;
    }

    async getModelSpec() {
        this.modelSpec = await this.call("webclient_model_spec");
    }

    // Syntax sugar RPC methods
}

class Environment {
    constructor(url) {
        this.url = url;
    }

    model(name) {
        return new Recordset(this, name, null, []);
    }

    async lookupXMLId(xmlid, model = null) {
        return await this.model("core.xmlid").call("lookup", [xmlid], {...(model && {model: model})});
    }
}

export const env = new Environment(window.location.origin + "/api/jsonrpc");
