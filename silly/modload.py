import logging
import importlib.util
import sys
import ast
from pathlib import Path
from lxml import etree
import silly

_logger = logging.getLogger(__name__)


def _import_py_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _validate_manifest(mdict):
    if not isinstance(mdict, dict):
        return False
    if not isinstance(mdict.get("dependencies"), list):
        return False
    if not isinstance(mdict.get("staticfiles"), dict):
        return False
    if not isinstance(mdict.get("data"), list):
        return False
    if not isinstance(mdict.get("version"), str) or len(mdict["version"]) == 0:
        return False
    return True


def load_datafile(env, fname):
    def load_record(el):
        model = el.attrib.get("model")
        id = int(el.attrib.get("id")) if el.attrib.get("id") else el.attrib.get("xmlid")
        noupdate = el.attrib["noupdate"] == "1" if "noupdate" in el.attrib else False

        vals = {}

        for x in el:
            if x.tag != "field":
                raise Exception(f"invalid tag {x.tag}")
            name = x.attrib["name"]
            eltext = x.text
            for child in x:
                if eltext is None:
                    eltext = ""
                eltext += (child.text if child.text is not None else "") + etree.tostring(
                    child
                ).decode("utf-8")
            match x.attrib["t"]:
                case "str":
                    vals[name] = eltext
                case "int":
                    vals[name] = int(x.text)
                case _:
                    raise Exception(f"unknown type {x.attrib['t']}")

        if isinstance(id, int):
            rec = env[model].browse(id)
        else:
            rec = env.xmlid_lookup(model, id)
            if rec and rec._name != model:
                # In case of model mismatch: overwrite the old xmlid and create a new record
                rec = env[model]  # empty recordset
        if not rec:
            rec = env[model].create(vals)
            if not isinstance(id, int):
                env["xmlid"].assign(id, rec, overwrite=True)
        elif not noupdate:
            rec.write(vals)

    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(fname, parser=parser)
    for el in tree.getroot():
        match el.tag:
            case "record":
                load_record(el)
            case _:
                raise Exception(f"unknown tag {el.tag}")


staticfiles = {}


def add_module_paths(paths):
    silly.modules.__path__ += paths


_data_to_load = []

_loaded_modules = []


def _load_module(name, env):
    if name in _loaded_modules:
        _logger.debug("will not load module %s again because it has already been loaded", name)
        return
    _loaded_modules.append(name)
    _logger.info("loading module %s", name)
    modpath = None
    for dir in silly.modules.__path__:
        p = Path(dir) / name
        if p.is_dir() and (p / "__manifest__.py").is_file() and (p / "__init__.py").is_file():
            modpath = p.resolve()
            break

    if modpath is None:
        raise Exception(f"could not find module {name}")

    _logger.debug("module %s from path %s", name, modpath)

    with open(modpath / "__manifest__.py", encoding="utf-8") as f:
        manifest = ast.literal_eval(f.read())
        if not _validate_manifest(manifest):
            raise Exception(f"manifest of {name} is invalid")

    for dep in manifest["dependencies"]:
        _logger.debug("loading dependency %s of module %s", dep, name)
        _load_module(dep, env)

    for k, v in manifest["staticfiles"].items():
        staticfiles[k] = modpath / "static" / v

    mod = _import_py_module(f"silly.modules.{name}", str(modpath / "__init__.py"))

    for d in manifest["data"]:
        _data_to_load.append(modpath / d)

    _logger.info("loaded module %s", name)

    return mod


_modules_to_load = []


def load_module(name):
    _modules_to_load.append(name)


def load_all(env):
    for name in _modules_to_load:
        _load_module(name, env)
    for mod in silly.model.models_to_register:
        env.register_model(mod)


def load_all_data(env):
    for f in _data_to_load:
        _logger.info("loading data file %s", f)
        load_datafile(env, f)


def unload_all():
    # models
    silly.model.models_to_register = []

    # modules
    global _modules_to_load
    global _data_to_load
    global _loaded_modules
    _modules_to_load = []
    _data_to_load = []
    _loaded_modules = []
    for mod in sys.modules.copy():
        if not mod.startswith("silly.modules."):
            continue
        _logger.debug("removing %s from sys.modules", mod)
        del sys.modules[mod]

    # TODO: routes
