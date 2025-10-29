import logging
import sillyorm
import sqlalchemy
from . import modload, model, globalvars
from .exceptions import SillyException

_logger = logging.getLogger(__name__)


class SillyRestartException(SillyException):
    pass


def load_all():
    with globalvars.registry.environment(autocommit=True) as env:
        modules_to_load = [m.name for m in env["core.module"].search([])]
    globalvars.registry.reset_full()
    _logger.info("unloading to prepare for init stage 2")
    modload.unload_all()
    _logger.info("silly load stage 2 (load all modules)")
    modload.load(globalvars.registry, ["core"] + modules_to_load)
    globalvars.registry.resolve_tables()
    globalvars.registry.init_db_tables(automigrate="none")
    _logger.info("silly load stage 2 finished")


def update(to_change, uninstall):
    with globalvars.registry.environment(autocommit=True) as env:
        installed_versions = {m.name: m.version for m in env["core.module"].search([])}

    if uninstall:
        if any(x not in installed_versions for x in to_change):
            raise Exception("attempted uninstalling something that isn't even installed :sob:")
        to_uninstall = modload.resolve_dependents(installed_versions, to_change)
        to_install = modload.resolve_dependencies(list(set(installed_versions) - set(to_uninstall)))
        if any(x in to_install for x in to_uninstall):
            raise Exception("tf?")
        for modname in to_uninstall:
            manifest = modload.get_manifest(modname)
            if installed_versions.get(modname) != manifest["version"]:
                raise Exception(
                    f"while uninstalling {modname}: attempted uninstalling a module that hasn't"
                    " been updated to the latest version!"
                )
        if any(x not in modload.loaded_modules for x in to_change):
            raise Exception("attempted uninstalling something that isn't loaded")
    else:
        to_uninstall = []
        to_install = modload.resolve_dependencies(to_change + list(installed_versions))

    ### CHECKS END HERE, DANGER STARTS HERE

    # if we are in a worker we signal the main process to shut down the workers and do the update, then just return
    if hasattr(globalvars.threadlocal, "main_process_queue"):
        globalvars.threadlocal.main_process_queue.put(["mod.update", to_change, uninstall])
        return

    # delete records associated with the modules we want to uninstall
    if uninstall:
        with globalvars.registry.environment(autocommit=True) as env:
            for modname in to_uninstall:
                for record in env["core.xmlid"].search([("source_module", "=", modname)]):
                    _logger.info(
                        "uninstall: deleting record with xmlid '%s' (%s ID %s) because it belongs"
                        " to module '%s'",
                        record.xmlid,
                        record.model_name,
                        record.model_id,
                        modname,
                    )
                    original_record = record.get()
                    if original_record:
                        original_record.delete()
                    record.delete()

    globalvars.registry.reset_full()
    _logger.info("silly update - unloading all modules")
    modload.unload_all()

    modload.load(globalvars.registry, to_install)

    globalvars.registry.resolve_tables()

    # up migrations
    for i, modname in enumerate(to_install):
        manifest = modload.get_manifest(modname)
        # not installed OR installed, getting an upgrade
        if modname not in installed_versions or manifest["version"] != installed_versions[modname]:
            modload.run_migrations(
                globalvars.registry, modname, installed_versions.get(modname), manifest["version"]
            )
            _logger.info("migrated module %s (%d/%d)", modname, i + 1, len(to_install))

    _logger.info("running automigrations")
    globalvars.registry.init_db_tables(automigrate="auto")

    # down migrations
    for i, modname in enumerate(to_uninstall):
        modload.run_migrations(
            globalvars.registry, modname, installed_versions.get(modname), "base", downgrade=True
        )
        _logger.info("down-migrated module %s (%d/%d)", modname, i + 1, len(to_uninstall))

    globalvars.registry.init_db_tables(automigrate="none")
    with globalvars.registry.environment(autocommit=True) as env:
        modload.load_all_data(env)

    # update module tables
    # if we uninstalle core, there are no tables to update..
    if "core" not in to_uninstall:
        with globalvars.registry.environment(autocommit=True) as env:
            for modname in to_install:
                manifest = modload.get_manifest(modname)
                rec = env["core.module"].search([("name", "=", modname)])
                if rec:
                    rec.version = manifest["version"]
                else:
                    env["core.module"].create(
                        {
                            "name": modname,
                            "version": manifest["version"],
                        }
                    )
            for modname in to_uninstall:
                rec = env["core.module"].search([("name", "=", modname)])
                rec.delete()

    # restart entirely, shits far too fcked otherwise
    # (imagine some module did monkeypatches! We want to make sure everything is in a sane state!)
    raise SillyRestartException("update finished")


def load_core(allow_core_init):
    _logger.info("silly load stage 1 (load core module)")
    # the core module is essential for installing other modules, so we **always** install it, no matter what
    if not sqlalchemy.inspect(globalvars.registry.engine).has_table("core_module"):
        if not allow_core_init:
            raise Exception(
                "Core module not installed, cannot install due to update being disabled"
            )
        _logger.info("Initializing database (installing core module)")
        modload.unload_all()
        modload.load(globalvars.registry, ["core"])
        globalvars.registry.resolve_tables()
        manifest = modload.get_manifest("core")
        modload.run_migrations(globalvars.registry, "core", None, manifest["version"])
        globalvars.registry.init_db_tables(automigrate="auto")
        with globalvars.registry.environment(autocommit=True) as env:
            modload.load_all_data(env)
            env["core.module"].create(
                {
                    "name": "core",
                    "version": manifest["version"],
                }
            )
        modload.unload_all()
        _logger.info("database initialized (core module installed successfully)")
    modload.unload_all()
    globalvars.registry.reset_full()
    modload.load(globalvars.registry, ["core"])
    globalvars.registry.resolve_tables()
    globalvars.registry.init_db_tables(automigrate="ignore", auto_create=False)
