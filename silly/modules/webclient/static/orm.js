import { jsonrpc } from "@tools/jsonrpc";

function jsonrpc_id() {
    return Math.floor(Math.random() * 0xFFFFFFFF);
}

function convORMJsonrpcType(environment, obj) {
    const isSillyRecordset = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyRecordset" && typeof obj.model === "string" && Array.isArray(obj.records);
    const isSillyFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyFieldValue" && typeof obj.type === "string";
    // TODO: actually convert field value types!
    if (isSillyFieldValue(obj)) {
        const vals = obj;
        vals.value = convORMJsonrpcType(environment, vals.value);
        return vals;
    }
    if (isSillyRecordset(obj)) {
        const ids = [];
        const fields = [];
        // accumulate ids and field values for the recordset, recurse into all field values and convert them
        for (const rec of obj.records) {
            ids.push(convORMJsonrpcType(environment, rec["id"].value));
            delete rec["id"];
            const fields_obj = {};
            for (const [key, value] of Object.entries(rec)) {
                fields_obj[key] = convORMJsonrpcType(environment, value);
            }
            fields.push(fields_obj);
        }
        return new Recordset(environment.model(obj.model), ids, fields).asProxy();
    }
    return obj;
}

class Recordset {
    constructor(model, ids, fields) {
        this.model = model;
        this.ids = ids;
        this.fields = fields;
    }

    async call(method, args = [], kwargs = {}) {
        const params = {
            model: this.model.name,
            fn: method,
            args: args,
            kwargs: kwargs,
            ids: this.ids,
        };
        let ret = await jsonrpc(this.model.env.url, "env_exec_ids", jsonrpc_id(), params);
        ret = convORMJsonrpcType(this.model.env, ret);
        return ret;
    }

    ensureOne() {
        if (this.ids.length != 1) {
            throw new Error(`ensureOne found ${this.ids.length}`);
        }
    }

    get id() {
        this.ensureOne();
        return this.ids[0];
    }

    getField(name) {
        this.ensureOne();
        return this.fields[0][name];
    }

    getFieldValue(name) {
        return this.getField(name).value;
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

    [Symbol.iterator]() {
        let idx = 0;
        const model = this.model;
        const ids = this.ids;
        const fields = this.fields;

        return {
            next: () => {
                if (idx < ids.length) {
                    let c_idx = idx++;
                    return { value: new Recordset(model, [ids[c_idx]], fields[c_idx]).asProxy(), done: false };
                } else {
                    return { done: true };
                }
            }
        };
    }
}



class Model {
    constructor(env, name) {
        this.env = env;
        this.name = name;
    }

    async call(method, args = [], kwargs = {}) {
        const params = {
            model: this.name,
            fn: method,
            args: args,
            kwargs: kwargs,
        };
        let ret = await jsonrpc(this.env.url, "env_exec", jsonrpc_id(), params);
        ret = convORMJsonrpcType(this.env, ret);
        return ret;
    }
}

class Environment {
    constructor(url) {
        this.url = url;
    }

    model(name) {
        return new Model(this, name);
    }
}

export const env = new Environment(window.location.origin + "/api/jsonrpc");
