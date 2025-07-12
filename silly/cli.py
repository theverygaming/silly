import argparse
import logging
from . import main, tests, modload, mod

_logger = logging.getLogger(__name__)


class SillyConfig:
    def __init__(self):
        self.connstr = None
        self.module_path = ["modules/"]

    def init_arg_parser(self, parser):
        parser.add_argument("--connstr", type=str, required=True)
        parser.add_argument("--module_path", nargs="+", type=str)

    def process_argparser_args(self, namespace):
        self.connstr = namespace.connstr or self.connstr
        self.module_path = namespace.module_path or self.module_path
        self.process_args()

    def process_args(self):
        modload.add_module_paths(self.module_path)


def cmd_run(config: SillyConfig):
    main.init(config.connstr)
    main.run()


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
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
    )
    logging.getLogger("silly").setLevel(logging.DEBUG)
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
