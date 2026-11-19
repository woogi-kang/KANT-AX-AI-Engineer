import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

LIST_SQL = """
SELECT c.course_id, s.sport_name, c.course_name, c.fee
FROM courses c
JOIN sports s ON c.sport_id = s.sport_id
ORDER BY c.course_id
"""


def list_courses(conn):
    for c in conn.execute(LIST_SQL):
        no = c["course_id"]
        fee = f"{c['fee']:,}원"
        print(f"{no:>2} | {c['sport_name']} | {fee:>8} | {c['course_name']}")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    list_courses(conn)
