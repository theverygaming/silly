import importlib.util
import sys
import ast
from pathlib import Path
import silly


def _import_py_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def _validate_manifest(mdict):
    if not isinstance(mdict, dict):
        return False
    if "dependencies" not in mdict:
        return False
    if not isinstance(mdict["dependencies"], list):
        return False
    if "staticfiles" not in mdict:
        return False
    if not isinstance(mdict["staticfiles"], dict):
        return False
    if "templates" not in mdict:
        return False
    if not isinstance(mdict["templates"], list):
        return False
    return True


staticfiles = {}
xmltemplates = []

def set_module_paths(paths):
    silly.modules.__path__ += paths

def load_module(name):
    print(f"loading module {name}...")
    modpath = None
    for dir in silly.modules.__path__:
        p = Path(dir) / name
        if p.is_dir() and (p / "__manifest__.py").is_file() and (p / "__init__.py").is_file():
            modpath = p.resolve()
            break

    if modpath is None:
        raise Exception(f"could not find module {name}")

    with open(modpath / "__manifest__.py", encoding="utf-8") as f:
        manifest = ast.literal_eval(f.read())
        if not _validate_manifest(manifest):
            raise Exception(f"manifest of {name} is invalid")
    
    for dep in manifest["dependencies"]:
        load_module(dep)

    for k, v in manifest["staticfiles"].items():
        staticfiles[k] = modpath / "static" / v
    
    for t in manifest["templates"]:
        xmltemplates.append(modpath / "templates" / t)

    mod = _import_py_module(f"silly.{name}", str(modpath / "__init__.py"))

    print(f"loaded module {name} ({mod})")

    return mod
