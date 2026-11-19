import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

with psycopg.connect(DSN) as conn:
    row = conn.execute("SELECT COUNT(*) FROM members").fetchone()
    print(row)
    print(row[0], "명")
    row = conn.execute("SELECT name FROM members WHERE member_id = 99").fetchone()
    print(row)
