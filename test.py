import silly
import sillyorm

if __name__ == "__main__":
    #conn = sillyorm.dbms.postgresql.PostgreSQLConnection(
    #    "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #)
    conn = sillyorm.dbms.sqlite.SQLiteConnection("test.db", check_same_thread=False)

    silly.main.init(conn)
    silly.modload.set_module_paths(["silly/data/modules/"])
    silly.modload.load_module("webclient")
    silly.modload.load_module("activitypub")
    silly.modload.load_module("webclient_nojs")
    silly.modload.load_module("webclient_nojs_samples")
    silly.main.run()
