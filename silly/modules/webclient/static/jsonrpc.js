export async function jsonrpc(url, method, id, params) {
    const resp = await fetch(url, {
        method: "POST",
        body: JSON.stringify({
            jsonrpc: "2.0",
            id: id,
            method: method,
            params: params
        }),
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
    });
    return (await resp.json()).result;
}
