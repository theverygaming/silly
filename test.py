import silly
import sillyorm

if __name__ == "__main__":
    #conn = sillyorm.dbms.postgresql.PostgreSQLConnection(
    #    "host=127.0.0.1 dbname=test user=postgres password=postgres"
    #)
    conn = sillyorm.dbms.sqlite.SQLiteConnection("test.db", check_same_thread=False)

    silly.main.init(conn)
    silly.modload.set_module_paths(["modules/"])
    silly.modload.load_module("webclient", silly.main.env)
    silly.modload.load_module("activitypub", silly.main.env)
    silly.main.run()
