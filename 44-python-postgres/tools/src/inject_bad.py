import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
name = "x' OR '1'='1"

with psycopg.connect(DSN) as conn:
    sql = f"SELECT name, phone FROM members WHERE name = '{name}'"
    print(sql)
    rows = conn.execute(sql).fetchall()
    print(len(rows), "명이 나왔어요")
