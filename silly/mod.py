import logging
import sillyorm
import sqlalchemy
from . import modload, model, globalvars

_logger = logging.getLogger(__name__)


class SillyRestartException(Exception):
    pass


def load_all():
    with globalvars.registry.environment(autocommit=True) as env:
        modules_to_load = [m.name for m in env["module"].search([])]
    globalvars.registry.reset_full()
    _logger.info("unloading to prepare for init stage 2")
    modload.unload_all()
    _logger.info("silly load stage 2 (load all modules)")
    modload.load(globalvars.registry, ["core"] + modules_to_load)
    globalvars.registry.resolve_tables()
    globalvars.registry.init_db_tables(automigrate="none")
    # TODO: i don't think we should be loading data on normal loads? Only on update...
    with globalvars.registry.environment(autocommit=True) as env:
        modload.load_all_data(env)
    _logger.info("silly load stage 2 finished")


def update(to_change, uninstall):
    with globalvars.registry.environment(autocommit=True) as env:
        installed_versions = {m.name: m.version for m in env["module"].search([])}

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
        # delete records associated with the modules we want to uninstall
        with globalvars.registry.environment(autocommit=True) as env:
            for modname in to_uninstall:
                for record in env["xmlid"].search([("source_module", "=", modname)]):
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
    else:
        to_uninstall = []
        to_install = modload.resolve_dependencies(to_change + list(installed_versions))

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

    # down migrations
    for i, modname in enumerate(to_uninstall):
        modload.run_migrations(
            globalvars.registry, modname, installed_versions.get(modname), "base", downgrade=True
        )
        # get rid of the versions table (alembic won't do this for us!)
        with globalvars.registry.engine.connect() as conn:
            table_name_esc = sqlalchemy.sql.compiler.IdentifierPreparer(
                globalvars.registry.engine.dialect
            ).quote(f"__silly_alembic_version_{modname}")
            conn.execute(sqlalchemy.sql.text(f"DROP TABLE IF EXISTS {table_name_esc}"))
        _logger.info("down-migrated module %s (%d/%d)", modname, i + 1, len(to_uninstall))

    # generate new migrations
    # TODO: dev only...
    modload.generate_migrations(globalvars.registry)

    globalvars.registry.init_db_tables(automigrate="none")
    with globalvars.registry.environment(autocommit=True) as env:
        modload.load_all_data(env)

    # update module tables
    with globalvars.registry.environment(autocommit=True) as env:
        for modname in to_install:
            manifest = modload.get_manifest(modname)
            rec = env["module"].search([("name", "=", modname)])
            if rec:
                rec.version = manifest["version"]
            else:
                env["module"].create(
                    {
                        "name": modname,
                        "version": manifest["version"],
                    }
                )
        for modname in to_uninstall:
            rec = env["module"].search([("name", "=", modname)])
            rec.delete()

    # restart entirely, shits far too fcked otherwise
    # (imagine some module did monkeypatches! We want to make sure everything is in a sane state!)
    raise SillyRestartException("update finished")


def load_core(allow_update):
    _logger.info("silly load stage 1 (load core module)")
    # the core module is essential for installing other modules, so we **always** install it, no matter what
    if not sqlalchemy.inspect(globalvars.registry.engine).has_table("module"):
        if not allow_update:
            raise Exception(
                "Core module not installed, cannot install due to update being disabled"
            )
        _logger.info("Initializing database (installing core module)")
        modload.unload_all()
        modload.load(globalvars.registry, ["core"])
        globalvars.registry.resolve_tables()
        manifest = modload.get_manifest("core")
        modload.run_migrations(globalvars.registry, "core", None, manifest["version"])
        # TODO: dev only...
        modload.generate_migrations(globalvars.registry, "core", manifest["version"])
        globalvars.registry.init_db_tables(automigrate="none")
        with globalvars.registry.environment(autocommit=True) as env:
            modload.load_all_data(env)
            env["module"].create(
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
    globalvars.registry.init_db_tables(automigrate="ignore")
    # TODO: i don't think we should be loading data on normal loads? Only on update...
    with globalvars.registry.environment(autocommit=True) as env:
        modload.load_all_data(env)
