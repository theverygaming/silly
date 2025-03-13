from lxml import etree

def process_xml_inheritance(root: str, extensions: list[str]):
    root_tree = etree.fromstring(root)
    for ext in extensions:
        ext_tree = etree.fromstring(ext)
        for xpath_el in ext_tree.xpath("//xpath"):
            for elem in root_tree.xpath(xpath_el.attrib["expr"]):
                match xpath_el.attrib["type"]:
                    case "after":
                        parent = elem.getparent()
                        idx = parent.index(elem)
                        for i, el in enumerate(xpath_el):
                            parent.insert(idx + 1 + i, el)
                        # TODO: what about text?
                    case _:
                        raise Exception(f"xpath: unknown type '{xpath_el.attrib['type']}'")
    return etree.tostring(root_tree, encoding="utf-8").decode("utf-8")
