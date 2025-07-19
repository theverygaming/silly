export class Registry {
    constructor() {
        this.map = {};
    }

    add(key, value) {
        if (typeof key != "string" || !key) {
            throw new Error("Invalid key");
        }
        if (key in this.map) {
            throw new Error(`Key ${key} is already in the registry`);
        }
        this.map[key] = value;
    }

    remove(key) {
        delete this.map[key];
    }

    get(key) {
        if (key in this.map) {
            return this.map[key];
        }
        throw new Error(`Key ${key} not in the registry`);
    }
}

export const registry = new Registry();

registry.add("viewComponents", new Registry());
