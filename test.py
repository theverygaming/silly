import logging

# this is here to make sure we get _all the logs_
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
    )
    logging.getLogger("silly").setLevel(logging.DEBUG)


import silly
import sillyorm

if __name__ == "__main__":
    #conn = sillyorm.dbms.postgresql.PostgreSQLConnection(
    #    "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #)
    conn = sillyorm.dbms.sqlite.SQLiteConnection("test.db", check_same_thread=False)

    silly.modload.add_module_paths(["modules/", "silly/modules/"])
    silly.main.init(
        conn,
        [
            "webclient",
            "activitypub",
            "webclient_nojs",
            "webclient_nojs_samples",
            "settings",
            "settings_views"
        ],
    )
    silly.main.run()
