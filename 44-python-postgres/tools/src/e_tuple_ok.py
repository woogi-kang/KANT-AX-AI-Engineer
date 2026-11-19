import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"
SQL = "SELECT COUNT(*) FROM enrollments WHERE enroll_month = %s"

with psycopg.connect(DSN) as conn:
    row = conn.execute(SQL, (MONTH,)).fetchone()
    print(row)
