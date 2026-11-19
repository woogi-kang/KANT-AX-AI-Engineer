import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"
MEMBER_ID = 10
COURSE_ID = 5

INSERT_SQL = """
INSERT INTO enrollments
  (enrollment_id, member_id, course_id, enroll_month, status, pay_amount)
VALUES
  ((SELECT MAX(enrollment_id) + 1 FROM enrollments), %s, %s, %s, '신청', %s)
"""


def enroll(conn, member_id, course_id):
    # 신청한 강좌의 수강료 꺼내기
    sql = "SELECT fee FROM courses WHERE course_id = %s"
    row = conn.execute(sql, (course_id,)).fetchone()
    fee = row["fee"]

    conn.execute(INSERT_SQL, (member_id, course_id, MONTH, fee))
    print(f"{member_id}번 회원이 {course_id}번 강좌를 신청했어요 ({fee:,}원)")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    enroll(conn, MEMBER_ID, COURSE_ID)
