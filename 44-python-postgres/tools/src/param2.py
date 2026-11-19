import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
SQL = "SELECT course_name, fee FROM courses WHERE fee BETWEEN %s AND %s ORDER BY fee"

with psycopg.connect(DSN, row_factory=dict_row) as conn:
    for c in conn.execute(SQL, (60000, 70000)):
        print(c["course_name"], c["fee"])
