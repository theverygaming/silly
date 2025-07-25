import logging
import collections
from . import modload


class SillyConfig:
    # dict of option tuples
    # each option tuple is:
    # (
    #     default value
    #     required - Falsy value for not required or a function that returns True if the required
    #                thing is fulfilled - this function will be called prior to the type conversion!
    #     type conversion function/constructor or None
    # )
    _CONFIG_OPTIONS = {
        "connstr": (None, lambda x: bool(x), str),
        "module_path": (["modules/"], False, list),
        "loglevel": ("INFO", False, lambda x: logging.getLevelNamesMapping()[x]),
        "workers-web": (1, False, int),
        "workers-cron": (1, False, int),
    }

    def __init__(self):
        # array of dicts, first one in the array has highest priority
        self._raw_cfg = [
            {},  # command-line arguments
            {},  # environent variables
            {},  # configuration file
            {k: v[0] for k, v in self._CONFIG_OPTIONS.items()},
        ]
        self._cfg_processed = None

    def __getitem__(self, key: str):
        if self._cfg_processed is None:
            raise Exception("arguments have never been processed!")
        if key not in self._cfg_processed:
            raise Exception(f"configuration is missing '{key}'")
        return self._cfg_processed[key]

    def argparse_init(self, parser):
        parser.add_argument("--connstr", type=str)
        parser.add_argument("--module_path", nargs="+", type=str)
        parser.add_argument(
            "--loglevel",
            type=str,
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
            default=self._CONFIG_OPTIONS["loglevel"][0],
        )

    def argparse_process(self, namespace):
        args = {
            "connstr": namespace.connstr,
            "module_path": namespace.module_path,
            "loglevel": namespace.loglevel,
        }
        self.set_cmdline_args(args)

    def set_cmdline_args(self, args):
        self._raw_cfg[0] = args

    def _parse_cfg(self):
        # get rid of unset args
        for i, args in enumerate(self._raw_cfg):
            # we don't get rid of stuff in the default config
            if i == len(self._raw_cfg) - 1:
                continue
            for key, value in list(args.items()):
                if value is None or value == "":
                    del self._raw_cfg[i][key]

        cfg = collections.ChainMap(*self._raw_cfg)

        final_cfg = {}

        # handle required args
        for k, v in self._CONFIG_OPTIONS.items():
            if not v[1]:  # v[1] -> required function
                continue
            if not v[1](cfg[k]):
                raise Exception(f"required argument '{k}' missing")

        # convert arg types
        for k, v in self._CONFIG_OPTIONS.items():
            if v[2]:  # v[2] -> type conversion function
                final_cfg[k] = v[2](cfg[k])
            else:
                final_cfg[k] = cfg[k]

        self._cfg_processed = final_cfg

    def apply_cfg(self):
        self._parse_cfg()
        modload.add_module_paths(self["module_path"])
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            level=(
                logging.INFO
                if logging.getLevelName(logging.INFO) >= logging.getLevelName(self["loglevel"])
                else self["loglevel"]
            ),
        )
        logging.getLogger("silly").setLevel(self["loglevel"])
