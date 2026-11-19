import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
SQL = "SELECT course_id, course_name, fee FROM courses LIMIT 3"

with psycopg.connect(DSN) as conn:
    rows = conn.execute(SQL).fetchall()
    print(rows)
    print(rows[0])
    print(rows[0][1])
    for row in rows:
        print(row[1], row[2])
