export class Bus {
    constructor() {
        this.listeners = new Set();
    }

    subscribe(cb) {
        this.listeners.add(cb);
        return () => this.listeners.delete(cb);
    }

    publish(data) {
        for (const cb of this.listeners) {
            cb(data);
        }
    }
}
