import { jsonrpc } from "@tools/jsonrpc";

function jsonrpc_id() {
    return Math.floor(Math.random() * 0xFFFFFFFF);
}

function convORMJsonrpcType(env, obj) {
    const isSillyRecordset = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyRecordset" && typeof obj.model === "string" && Array.isArray(obj.records) && typeof obj.spec === "object";
    if (isSillyRecordset(obj)) {
        return Recordset.deserialize(env, obj);
    }
    return obj;
}

class Recordset {
    constructor(env, model, modelSpec, fields, fieldCacheDirty=false, editHistory=null) {
        this.env = env;
        this.model = model;
        this.modelSpec = modelSpec;
        this._fieldCache = fields;
        this._fieldCacheDirty = fieldCacheDirty;
        this._editHistory = editHistory ? editHistory : [];
    }

    // Serialization & Deserialization

    static deserialize(env, obj) {
        const isSillyFieldValue = (obj) => typeof obj === "object" && obj !== null && obj.objtype === "sillyFieldValue";
        const fields = [];
        for (const rec of obj.records) {
            const fields_obj = {};
            for (let [key, value] of Object.entries(rec)) {
                if (!isSillyFieldValue(value)) {
                    throw new Error("recordset value is not a sillyFieldValue");
                }
                //value.type = obj.spec.field_info[key].type;
                //value.rel_model = obj.spec.field_info[key].rel_model;
                // TODO: actually convert field value types!
                fields_obj[key] = convORMJsonrpcType(env, value.value);
            }
            fields.push(fields_obj);
        }
        return new Recordset(env, obj.model, obj.spec, fields).asProxy();
    }

    serialize(deserializeable=false) {
        this._ensureIsRWAble();
        // TODO: support nested recordsets
        const obj = {
            objtype: "sillyRecordset",
            model: this.model,
            records: [],
        }
        if (deserializeable) {
            obj.spec = this.modelSpec;
        }

        for (const fc of this._fieldCache) {
            const rs = {};
            for (const [key, value] of Object.entries(fc)) {
                rs[key] = {
                    objtype: "sillyFieldValue",
                    value: value,
                };
            }
            obj.records.push(rs);
        }

        return obj;
    }

    // Recordset methods

    _ensureIsRWAble() {
        if (!this.modelSpec) {
            throw new Error("_ensureIsRWAble: missing model spec");
        }
    }

    ensureOne() {
        if (this.getNRecords() != 1) {
            throw new Error(`ensureOne found ${this.getNRecords()} IDs in recordset`);
        }
    }

    async cacheFields(fields, cached = true) {
        if (this._fieldCacheDirty) {
            throw new Error("won't overwrite fields on unsaved recordset");
        }
        
        // filter out any fields that are already cached
        let fieldsToRead = fields;
        if (cached) {
            fieldsToRead = fields.filter(field => 
                !this._fieldCache.every((x) => (field in x))
            );
        }

        // no fields to read? abort 
        if (!fieldsToRead.length) {
            return;
        }

        const res = await this.call("webclient_read", [fieldsToRead], {});
        for (let idx = 0; idx < this._fieldCache.length; idx++) {
            const rec = res.getRecordById(this._fieldCache[idx].id);
            for (const field of fieldsToRead) {
                this._fieldCache[idx][field] = rec.getFieldCached(field);
            }
        }
    }

    clearFieldCache(discard_changes=false) {
        if (this._fieldCacheDirty && !discard_changes) {
            throw new Error("won't overwrite fields on unsaved recordset");
        }
        this._fieldCache = this._fieldCache.map(f => ({id: f.id}));
    }

    async getField(name, cached = true) {
        this.ensureOne();
        return (await this.getFieldMulti(name, cached))[0];
    }

    async getFieldMulti(name, cached = true) {
        if (this.getNRecords()) {
            this._ensureIsRWAble();
        }
        await this.cacheFields([name], cached);
        return this.getFieldCachedMulti(name);
    }

    getFieldCached(name) {
        this.ensureOne();
        return this.getFieldCachedMulti(name)[0];
    }

    getFieldCachedMulti(name) {
        if (this.getNRecords()) {
            this._ensureIsRWAble();
        }
        return this._fieldCache.map(f => {
            if (!(name in f)) {
                throw new Error(`Field '${name}' is not cached`);
            }
            return f[name];
        });
    }

    setField(name, value) {
        this.ensureOne();
        this._ensureIsRWAble();
        this._editHistory.push(this._fieldCache);
        this._fieldCache[0][name] = value;
        this._fieldCacheDirty = true;
    }

    getFieldSpec(name) {
        this._ensureIsRWAble();
        return this.modelSpec.field_info[name];
    }

    asProxy() {
        return new Proxy(this, {
            get(target, prop, receiver) {
                if (!(prop in target) && target.getNRecords() == 1 && target.modelSpec && prop in target.modelSpec.field_info) {
                    return target.getFieldCached(prop);
                }
                return Reflect.get(...arguments);
            },
        });
    }

    getRecordAtIdx(idx) {
        if (idx >= this.getNRecords()) {
            throw new Error(`cannot get record at index ${idx}, there are only ${this.getNRecords()} records in this recordset`);
        }
        // FIXME: it turns out if we pass the field cache like this the same object will be passed onto the children.. We don't really want that
        // as then when you change a child value the parent value changes and it shits itself fairly badly
        return new Recordset(this.env, this.model, this.modelSpec, [structuredClone(this._fieldCache[idx])], this._fieldCacheDirty, structuredClone(this._editHistory)).asProxy();
    }

    getRecordById(id) {
        const idx = this._fieldCache.findIndex(f => f.id === id);
        return this.getRecordAtIdx(idx);
    }

    getNRecords() {
        return this._fieldCache.length;
    }

    async save() {
        if (!this._fieldCacheDirty) {
            return;
        }
        console.log(this.serialize());
        //await this.call("webclient_write", [this.serialize()], {});
        this._fieldCacheDirty = false;
        this._editHistory = [];
    }

    hasUnsavedChanges() {
        return this._fieldCacheDirty;
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

    async call(method, args = [], kwargs = {}, conv = true, dirty_ok = false) {
        if (this._fieldCacheDirty && !dirty_ok) {
            throw new Error("can't call function on unsaved recordset");
        }
        const params = {
            model: this.model,
            fn: method,
            args: args,
            kwargs: kwargs,
        };
        const has_records = this.getNRecords() > 0;
        if (has_records) {
            params.ids = this.getFieldCachedMulti("id");
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
