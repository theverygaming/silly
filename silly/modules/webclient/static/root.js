import { h, render } from "@preact";

// Create your app
const app = h("div", null, "Hello World!", h("div", null, "2Hello World!", h("h1", null, "Hello World!"), h("h1", null, "Hello World!")));

render(app, document.body);
