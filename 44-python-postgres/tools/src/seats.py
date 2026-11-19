import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"

SEATS_SQL = """
SELECT c.course_id, c.course_name, c.capacity, COUNT(e.enrollment_id) AS taken
FROM courses c
LEFT JOIN enrollments e
  ON e.course_id = c.course_id AND e.enroll_month = %s AND e.status <> '취소'
GROUP BY c.course_id, c.course_name, c.capacity
ORDER BY c.course_id
"""


def list_seats(conn):
    print(MONTH, "남은 자리")
    for c in conn.execute(SEATS_SQL, (MONTH,)):
        left = c["capacity"] - c["taken"]
        print(f"{c['course_id']:>2} | {left:>2}자리 | {c['course_name']}")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    list_seats(conn)
