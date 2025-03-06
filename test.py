import sys
import os
import logging
import silly
import sillyorm

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
    )
    logging.getLogger("silly").setLevel(logging.DEBUG)
    # conn = sillyorm.dbms.postgresql.PostgreSQLConnection(
    #     "host=127.0.0.1 dbname=test user=postgres password=postgres"
    # )
    conn = sillyorm.dbms.sqlite.SQLiteConnection("test.db", check_same_thread=False)
    silly.modload.add_module_paths(["modules/"])
    try:
        silly.main.init(
            conn,
            [
                "webclient",
                "activitypub",
                "webclient_nojs",
                "webclient_nojs_samples",
                "settings",
                "settings_views",
            ],
            [],
            "no_update" not in sys.argv,
        )
    except silly.mod.SillyRestartException as e:
        argv = sys.argv
        if str(e) == "update finished":
            argv.append("no_update")

        executable = sys.executable
        if not argv or argv[0] != executable:
            argv.insert(0, executable)
        os.execve(sys.executable, argv, os.environ)
    silly.main.run()
