import argparse
import os
import sys
import logging
from . import main, tests, modload, mod

_logger = logging.getLogger(__name__)


class SillyConfig:
    _LOGLEVEL_MAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
    }

    _DEFAULTS = {
        "connstr": None,
        "module_path": ["modules/"],
        "loglevel": _LOGLEVEL_MAP["debug"],
    }

    def __init__(self):
        self.connstr = self._DEFAULTS["connstr"]
        self.module_path = self._DEFAULTS["module_path"]
        self.loglevel = self._DEFAULTS["loglevel"]

    def init_arg_parser(self, parser):
        parser.add_argument("--connstr", type=str, required=True)
        parser.add_argument("--module_path", nargs="+", type=str)
        parser.add_argument(
            "--loglevel", type=str, choices=("debug", "info", "warning"), default="info"
        )

    def process_argparser_args(self, namespace):
        self.connstr = namespace.connstr or self.connstr
        self.module_path = namespace.module_path or self.module_path
        self.loglevel = self._LOGLEVEL_MAP[namespace.loglevel]
        self.process_args()

    def process_args(self):
        modload.add_module_paths(self.module_path)
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
        )
        logging.getLogger("silly").setLevel(self.loglevel)


def reexec(executable=None, argv=None):
    if argv is None:
        argv = sys.argv
    if executable is None:
        executable = sys.executable

    if not argv or argv[0] != executable:
        argv.insert(0, executable)
    os.execve(executable, argv, os.environ)


def cmd_run(config: SillyConfig, do_reexec=True):
    main.init(config.connstr)
    try:
        main.run()
    except mod.SillyRestartException:
        if do_reexec:
            reexec()
        else:
            raise


def cmd_test(config: SillyConfig):
    main.init(config.connstr)
    tests.run_all_tests()


def cmd_update(config: SillyConfig, modules: list[str], throw_exc=False):
    _logger.info("updating/installing modules: %s", ", ".join(modules))
    try:
        main.init(config.connstr, modules_to_install=modules, update=True)
    except mod.SillyRestartException:
        if throw_exc:
            raise
    _logger.info("finished updating/installing")


def cmd_uninstall(config: SillyConfig, modules: list[str], throw_exc=False):
    _logger.info("uninstalling modules: %s", ", ".join(modules))
    try:
        main.init(config.connstr, modules_to_uninstall=modules, update=True)
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
    config.init_arg_parser(parser)

    # operations
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("run")
    subparsers.add_parser("test")
    subparsers.add_parser("update").add_argument("--modules", nargs="+", type=str, required=True)
    subparsers.add_parser("uninstall").add_argument("--modules", nargs="+", type=str, required=True)

    parsed_args = parser.parse_args(args[1:])
    config.process_argparser_args(parsed_args)
    match parsed_args.operation:
        case "run":
            cmd_run(config)
        case "test":
            cmd_test(config)
        case "update":
            cmd_update(config, parsed_args.modules)
        case "uninstall":
            cmd_uninstall(config, parsed_args.modules)
