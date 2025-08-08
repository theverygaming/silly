import argparse
import os
import sys
import logging
from . import main, tests, mod
from .config import SillyConfig

_logger = logging.getLogger(__name__)


def reexec(executable=None, argv=None):
    if argv is None:
        argv = sys.argv
    if executable is None:
        executable = sys.executable

    if not argv or argv[0] != executable:
        argv.insert(0, executable)
    os.execve(executable, argv, os.environ)


def cmd_run(config: SillyConfig, do_reexec=True):
    main.init(config)
    try:
        main.run(config)
    except mod.SillyRestartException:
        if do_reexec:
            reexec()
        else:
            raise


def cmd_test(config: SillyConfig):
    main.init(config)
    result = tests.run_all_tests()
    if not result.wasSuccessful():
        raise Exception(f"Tests failed!")


def cmd_repl(config: SillyConfig, do_reexec=True):
    main.init(config)
    try:
        main.repl(config)
    except mod.SillyRestartException:
        if do_reexec:
            reexec()
        else:
            raise


def cmd_update(config: SillyConfig, modules: list[str], throw_exc=False):
    _logger.info("updating/installing modules: %s", ", ".join(modules))
    try:
        main.init(config, modules_to_install=modules, update=True)
    except mod.SillyRestartException:
        if throw_exc:
            raise
    _logger.info("finished updating/installing")


def cmd_uninstall(config: SillyConfig, modules: list[str], throw_exc=False):
    _logger.info("uninstalling modules: %s", ", ".join(modules))
    try:
        main.init(config, modules_to_uninstall=modules, update=True)
    except mod.SillyRestartException:
        if throw_exc:
            raise
    _logger.info("finished uninstalling")


def entry(args):
    config = SillyConfig()
    parser = argparse.ArgumentParser(
        description="meow",
        epilog=":3",
        prog=args[0],
    )
    config.argparse_init(parser)

    # operations
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("run")
    subparsers.add_parser("test")
    subparsers.add_parser("repl")
    subparsers.add_parser("update").add_argument("--modules", nargs="+", type=str, required=True)
    subparsers.add_parser("uninstall").add_argument("--modules", nargs="+", type=str, required=True)

    parsed_args = parser.parse_args(args[1:])
    config.argparse_process(parsed_args)
    match parsed_args.operation:
        case "run":
            cmd_run(config)
        case "test":
            cmd_test(config)
        case "repl":
            cmd_repl(config)
        case "update":
            cmd_update(config, parsed_args.modules)
        case "uninstall":
            cmd_uninstall(config, parsed_args.modules)


def entry_noargs():
    entry(sys.argv)
