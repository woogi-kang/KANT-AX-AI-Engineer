import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
SQL = "SELECT course_id, course_name, fee FROM courses LIMIT 3"

with psycopg.connect(DSN, row_factory=dict_row) as conn:
    rows = conn.execute(SQL).fetchall()
    print(rows[0])
    for c in rows:
        print(c["course_name"], c["fee"])
