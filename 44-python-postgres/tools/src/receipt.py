import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"

RECEIPT_SQL = """
SELECT m.name, c.course_name, e.pay_amount
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
JOIN courses c ON e.course_id = c.course_id
WHERE e.member_id = %s AND e.enroll_month = %s AND e.status <> '취소'
ORDER BY e.enrollment_id
"""


def receipt(conn, member_id):
    rows = conn.execute(RECEIPT_SQL, (member_id, MONTH)).fetchall()
    print(f"{rows[0]['name']} 회원님의 {MONTH} 신청 내역")
    for r in rows:
        print(f"  {r['pay_amount']:>7,}원  {r['course_name']}")
    total = sum([r["pay_amount"] for r in rows])
    print(f"  {total:>7,}원  합계 ({len(rows)}개)")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    receipt(conn, 26)
