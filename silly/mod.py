import logging
import sillyorm
from . import modload, model, globalvars

_logger = logging.getLogger(__name__)


class SillyRestartException(Exception):
    pass


class CustomEnvironment(sillyorm.Environment):
    pass

def load_all(cursor):
    modules_to_load = [m.name for m in globalvars.env["module"].search([])]
    globalvars.env = None  # invalidate global environment
    _logger.info("unloading to prepare for init stage 2")
    modload.unload_all()
    _logger.info("silly load stage 2 (load all modules)")
    globalvars.env = CustomEnvironment(cursor, update_tables=False)
    modload.load(globalvars.env, ["core"] + modules_to_load)
    globalvars.env.init_tables()
    modload.load_all_data(globalvars.env)
    _logger.info("silly load stage 2 finished")


def update(to_change, uninstall):
    installed_versions = {m.name: m.version for m in globalvars.env["module"].search([])}

    if uninstall:
        if any(x not in installed_versions for x in to_change):
            raise Exception("attempted uninstalling something that isn't even installed :sob:")
        to_uninstall = modload.resolve_dependents(installed_versions, to_change)
        to_install = modload.resolve_dependencies(list(set(installed_versions) - set(to_uninstall)))
        if any(x in to_install for x in to_uninstall):
            raise Exception("tf?")
        if any(x not in modload.loaded_modules for x in to_change):
            raise Exception("attempted uninstalling something that isn't loaded")
        # delete records associated with the module
        for modname in to_uninstall:
            for record in globalvars.env["xmlid"].search([("source_module", "=", modname)]):
                _logger.info("uninstall: deleting record with xmlid '%s' (%s ID %s) because it belongs to module '%s'", record.xmlid, record.model_name, record.model_id, modname)
                original_record = record.get()
                if original_record:
                    original_record.delete()
                record.delete()
    else:
        to_uninstall = []
        to_install = modload.resolve_dependencies(to_change + list(installed_versions))

    cursor = globalvars.env.cr
    globalvars.env = None  # invalidate global environment
    _logger.info("silly update - unloading all modules")
    modload.unload_all()

    # pre-migrations
    for modname in to_install:
        manifest = modload.get_manifest(modname)
        # installed, getting an upgrade
        if modname in installed_versions and manifest["version"] != installed_versions[modname]:
            modload.run_migrations(
                cursor, modname, "pre", installed_versions[modname], manifest["version"]
            )
            cursor.commit()

    # sillyORM automatic upgrade
    env_update = CustomEnvironment(cursor, update_tables=True)
    modload.load(env_update, to_install)
    env_update.init_tables()
    modload.load_all_data(env_update)

    # post-migrations
    for modname in to_install:
        manifest = modload.get_manifest(modname)
        # installed, getting an upgrade
        if modname in installed_versions and manifest["version"] != installed_versions[modname]:
            modload.run_migrations(
                cursor, modname, "post", installed_versions[modname], manifest["version"]
            )
            cursor.commit()

    # update module tables
    for modname in to_install:
        manifest = modload.get_manifest(modname)
        rec = env_update["module"].search([("name", "=", modname)])
        if rec:
            rec.version = manifest["version"]
        else:
            env_update["module"].create(
                {
                    "name": modname,
                    "version": manifest["version"],
                }
            )
    for modname in to_uninstall:
        rec = env_update["module"].search([("name", "=", modname)])
        rec.delete()

    # restart entirely, shits far too fcked otherwise (fully unloading and re-loading things is far too complicated for now)
    raise SillyRestartException("update finished")


def load_core(cursor, allow_update):
    _logger.info("silly load stage 1 (load core module)")
    # the core module is essential for installing other modules, so we **always** install it, no matter what
    if not cursor._table_exists("module"):
        if not allow_update:
            raise Exception("Core module not installed, cannot install due to update being disabled")
        _logger.info("core module is not installed, installing automatically...")
        modload.unload_all()
        env_initial = CustomEnvironment(cursor, update_tables=True)
        modload.load(env_initial, ["core"])
        env_initial.init_tables()
        modload.load_all_data(env_initial)
        manifest = modload.get_manifest("core")
        env_initial["module"].create(
            {
                "name": "core",
                "version": manifest["version"],
            }
        )
        modload.unload_all()
        _logger.info("core module has been installed")
    modload.unload_all()
    env_initial = CustomEnvironment(cursor, update_tables=allow_update)
    modload.load(env_initial, ["core"])
    env_initial.init_tables()
    modload.load_all_data(env_initial)
    globalvars.env = env_initial
