import logging
import importlib.util
import sys
import ast
import re
import glob
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


def _load_datafile(env, fname, modname):
    def load_record(el):
        model = el.attrib["model"]
        xmlid = el.attrib["xmlid"]
        noupdate = el.attrib.get("noupdate") == "1"

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

        rec = env["xmlid"].lookup(model, xmlid)
        if rec and rec._name != model:
            # In case of model mismatch: overwrite the old xmlid and create a new record
            rec = env[model]  # empty recordset
        if not rec:
            rec = env[model].create(vals)
            if not isinstance(xmlid, int):
                env["xmlid"].assign(xmlid, rec, overwrite=True)
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

loaded_modules = []


def _find_module(name):
    modpath = None
    for dir in silly.modules.__path__:
        p = Path(dir) / name
        if p.is_dir() and (p / "__manifest__.py").is_file() and (p / "__init__.py").is_file():
            modpath = p.resolve()
            break

    if modpath is None:
        raise Exception(f"could not find module {name}")
    return modpath


def _load_module(name, env):
    if name in loaded_modules:
        raise Exception(f"attempted to load module '{name}' twice")
    loaded_modules.append(name)
    modpath = _find_module(name)

    _logger.debug("module %s from path %s", name, modpath)

    manifest = get_manifest(name)

    for dep in manifest["dependencies"]:
        if dep not in loaded_modules:
            raise Exception(
                f"attempted to load module '{name}' without loading the dependency '{dep}'"
                " beforehand"
            )

    for k, v in manifest["staticfiles"].items():
        staticfiles[k] = modpath / "static" / v

    mod = _import_py_module(f"silly.modules.{name}", str(modpath / "__init__.py"))

    for d in manifest["data"]:
        _data_to_load.append((modpath / d, name))

    return mod


def load(env, modules):
    resolved = resolve_dependencies(modules)
    for i, name in enumerate(resolved):
        _logger.info("loading module %s (%d/%d)", name, i + 1, len(resolved))
        _load_module(name, env)

    for mod in silly.model.models_to_register:
        env.register_model(mod)


def load_all_data(env):
    for i, (fname, mname) in enumerate(_data_to_load):
        _logger.info("loading data file %s from module %s (%d/%d)", fname, mname, i + 1, len(_data_to_load))
        _load_datafile(env, fname, mname)


def unload_all():
    # models
    silly.model.models_to_register = []

    # modules
    global staticfiles
    global _data_to_load
    global loaded_modules
    staticfiles = {}
    _data_to_load = []
    loaded_modules = []
    for mod in sys.modules.copy():
        if not mod.startswith("silly.modules."):
            continue
        _logger.debug("removing %s from sys.modules", mod)
        del sys.modules[mod]

    silly.http.Router.direct_children = []


def get_manifest(name):
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

    def _manifest_defaults(mdict):
        defaults = {}
        for k, v in defaults:
            if k not in mdict:
                mdict[k] = v
        return mdict

    modpath = _find_module(name)

    with open(modpath / "__manifest__.py", encoding="utf-8") as f:
        manifest = ast.literal_eval(f.read())
        if not _validate_manifest(manifest):
            raise Exception(f"manifest of {name} is invalid")
    return _manifest_defaults(manifest)


def run_migrations(cr, name, mtype, current_version, to_version):
    if mtype not in ["pre", "post"]:
        raise Exception(f"unknown migration type {mtype}")
    modpath = _find_module(name)

    scripts = glob.glob(str(modpath / "migrations" / to_version) + f"/{mtype}-*.py")

    for script in scripts:
        path = Path(script)
        _logger.info("running %s %s-migration %s to version %s", name, mtype, path.stem, to_version)
        spec = importlib.util.spec_from_file_location(
            f"silly.modules.{name}.migrations.{to_version}.{re.sub(r'\W+', '_', path.stem)}",
            str(path),
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        fn = getattr(module, "run", None)
        if fn is not None:
            fn(cr, current_version)


def resolve_dependencies(modules, resolved=None, seen=None):
    """
    Returns all modules that need to be loaded for the specified list of modules to get loaded
    """
    is_first_call = resolved is None and seen is None

    if is_first_call:
        resolved = []

    for name in sorted(set(modules)):
        if is_first_call:
            seen = set()

        if name not in resolved and name in seen:
            raise Exception(f"circular dependency detected: {name}")

        seen.add(name)
        manifest = get_manifest(name)

        for dep in manifest["dependencies"]:
            resolve_dependencies([dep], resolved, seen)

        if name not in resolved:
            resolved.append(name)

    # this is simply a sanity check for the above code, it can be removed sometime:tm:
    if is_first_call:
        all_loaded = []
        for mod in resolved:
            if mod in all_loaded:
                raise Exception(f"module {mod} loaded twice")
            deps = get_manifest(mod)["dependencies"]
            for dep in deps:
                if dep not in all_loaded:
                    raise Exception(f"module {mod} missing dependency {dep}")
            all_loaded.append(mod)

    return resolved


def resolve_dependents(all_modules, modules):
    depends_on = {}
    for modname in set(all_modules):
        manifest = get_manifest(modname)
        depends_on[modname] = manifest["dependencies"]

    def find_direct_dependents(module):
        return set([name for name, deps in depends_on.items() if module in deps])

    def find_dependents(modules_find, dependents=None):
        if dependents is None:
            dependents = set()
        dependents |= set(modules_find)

        new_dependents = set()
        for modname in modules_find:
            new_dependents |= find_direct_dependents(modname)
        dependents |= new_dependents
        if len(new_dependents) == 0:
            return dependents
        return find_dependents(new_dependents, dependents)

    return list(find_dependents(modules))
