import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"

INSERT_SQL = """
INSERT INTO enrollments
  (enrollment_id, member_id, course_id, enroll_month, status, pay_amount)
VALUES
  ((SELECT MAX(enrollment_id) + 1 FROM enrollments), %s, %s, %s, '신청', %s)
"""
FEE_SQL = "SELECT fee FROM courses WHERE course_id = %s"
DONE_SQL = """
SELECT enrollment_id FROM enrollments
WHERE member_id = %s AND course_id = %s AND enroll_month = %s
"""


def enroll(conn, member_id, course_id):
    row = conn.execute(FEE_SQL, (course_id,)).fetchone()
    if not row:
        print(f"{course_id}번 강좌는 없어요")
        return
    if conn.execute(DONE_SQL, (member_id, course_id, MONTH)).fetchone():
        print(f"{course_id}번 강좌는 이미 신청했어요")
        return
    conn.execute(INSERT_SQL, (member_id, course_id, MONTH, row["fee"]))
    print(f"{course_id}번 강좌를 신청했어요 ({row['fee']:,}원)")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    enroll(conn, 10, 30)
    enroll(conn, 10, 5)
    enroll(conn, 10, 5)
