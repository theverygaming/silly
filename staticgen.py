import json
import shutil
from pathlib import Path
from lxml import etree


Path("./silly/static").mkdir()

files = {
    "js": [],
    "xml": [],
}

for file in list(Path("./silly/frontend").glob("**/*")):
    if not file.is_file():
        continue
    match file.suffix:
        case ".js":
            files["js"].append(file)
        case ".xml":
            files["xml"].append(file)
        case _:
            (Path("./silly/static") / file.parents[0]).mkdir(parents=True, exist_ok=True)
            shutil.copy(file, Path("./silly/static") / file)

importmap = {
    "imports": {}
}

Path("./silly/static/js").mkdir()
for file in files["js"]:
    p = file.parent.relative_to("./silly/frontend") / file.name
    importmap["imports"][f"@{str(p.with_suffix(''))}"] = "./js/" + str(p)

    (Path("./silly/static/js") / p.parents[0]).mkdir(parents=True, exist_ok=True)
    shutil.copy(file, Path("./silly/static/js") / p)

xml_out = etree.Element("templates")
xmlparser = etree.XMLParser(remove_comments=True)
for file in files["xml"]:
    tree = etree.parse(file, parser=xmlparser)
    for child in tree.getroot():
        xml_out.append(child)

Path("./silly/static/xml").mkdir()
etree.ElementTree(xml_out).write("./silly/static/xml/templates.xml", xml_declaration=True)

with open("./silly/static/index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>test</title>

    <script type="importmap">{json.dumps(importmap)}</script>
    <script type="module" src="./js/root.js"></script>
  </head>
  <body>
  </body>
</html>
""")
