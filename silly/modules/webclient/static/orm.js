import { jsonrpc } from "@jsonrpc";

function jsonrpc_id() {
    return Math.floor(Math.random() * 0xFFFFFFFF);
}

function convORMJsonrpcType(environment, obj) {
    const isSillyRecordset = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyRecordset" && typeof obj.model === "string" && Array.isArray(obj.records);
    const isSillyFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyFieldValue" && typeof obj.type === "string";
    // TODO: actually convert field value types!
    if (isSillyFieldValue(obj)) {
        return convORMJsonrpcType(environment, obj.value);
    }
    if (isSillyRecordset(obj)) {
        const ids = [];
        const fields = [];
        // accumulate ids and field values for the recordset, recurse into all field values and convert them
        for (const rec of obj.records) {
            ids.push(convORMJsonrpcType(environment, rec["id"]));
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
    constructor(model, ids, field_values) {
        this.model = model;
        this.ids = ids;
        this.field_values = field_values;
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
        return this.field_values[0][name];
    }

    asProxy() {
        return new Proxy(this, {
            get(target, prop, receiver) {
                if (!(prop in target) &&target.ids.length == 1 && prop in target.field_values[0]) {
                    return target.getField(prop);
                }
                return Reflect.get(...arguments);
            },
        });
    }

    [Symbol.iterator]() {
        let idx = 0;
        const model = this.model;
        const ids = this.ids;
        const field_values = this.field_values;

        return {
            next: () => {
                if (idx < ids.length) {
                    let c_idx = idx++;
                    return { value: new Recordset(model, [ids[c_idx]], field_values[c_idx]).asProxy(), done: false };
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
