export function saneXpath(xmldoc, xpath) {
    const results = [];
    let it = xmldoc.evaluate(xpath, xmldoc);
    let node = it.iterateNext();
    while (node) {
        results.push(node);
        node = it.iterateNext();
    }
    if (results.length == 0) {
        return null;
    }
    return results
}
