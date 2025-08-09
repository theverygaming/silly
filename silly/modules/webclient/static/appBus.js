import { Bus } from "@bus";

export const appBus = new Bus();

export const MESSAGE_TYPES = Object.freeze({
    LOADING: "loading",
});

export class AppBusMessage {
    constructor(type, data) {
        this.type = type;
        this.data = data;
    }
}

export function loadingNotif(msg) {
    appBus.publish(new AppBusMessage(
        MESSAGE_TYPES.LOADING,
        {msg, state: true},
    ));
    const finish = () => {
        appBus.publish(new AppBusMessage(
            MESSAGE_TYPES.LOADING,
            {msg, state: false},
        )); 
    };
    return finish;
}

export async function loadingNotifAsync(msg, fn) {
    const done = loadingNotif(msg);
    try {
        const res = await fn();
        return res;
    } finally {
        done();
    }
}

export function loadingNotifPromise(msg, promise) {
  return loadingNotifAsync(msg, () => {
    return promise;
  });
}
