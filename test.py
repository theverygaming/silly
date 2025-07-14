import sys
import logging
import silly


if __name__ == "__main__":
    config = silly.config.SillyConfig()
    config.set_cmdline_args({
        "loglevel": "INFO",
        "connstr": "sqlite:///test.db",
    })

    try:
        if "no_update" not in sys.argv:
            silly.cli.cmd_update(
                config,
                [
                    "webclient",
                    "activitypub",
                    "settings",
                    "jsonrpc",
                    "profiler",
                    "cron",
                    "cron_samples",
                    "modulemanager",
                ],
                throw_exc=True,
            )
        else:
            silly.cli.cmd_run(
                config,
                do_reexec=False,
            )
    except silly.mod.SillyRestartException as e:
        argv = sys.argv
        if str(e) == "update finished":
            argv.append("no_update")
        silly.cli.reexec(argv=argv)
