import logging
import silly
import sillyorm

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.DEBUG
    )
    #conn = sillyorm.dbms.postgresql.PostgreSQLConnection(
    #    "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #)
    conn = sillyorm.dbms.sqlite.SQLiteConnection("test.db", check_same_thread=False)

    silly.main.init(conn)
    silly.modload.add_module_paths(["modules/", "silly/modules/"])
    silly.modload.load_module("webclient")
    silly.modload.load_module("activitypub")
    silly.modload.load_module("webclient_nojs")
    silly.modload.load_module("webclient_nojs_samples")
    silly.modload.load_module("settings")
    silly.modload.load_module("settings_views")
    silly.main.run()
