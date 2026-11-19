import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

SQL = """
SELECT c.course_name, c.fee
FROM courses c
JOIN sports s ON c.sport_id = s.sport_id
WHERE s.sport_name = %s
"""


def show(conn, sport):
    print("종목:", sport)
    for c in conn.execute(SQL, (sport,)):
        print("  ", c["course_name"], c["fee"])


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    show(conn, "테니스")
    show(conn, "요가")
