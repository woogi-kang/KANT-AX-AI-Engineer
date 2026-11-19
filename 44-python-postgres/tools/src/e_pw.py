import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin123"

with psycopg.connect(DSN) as conn:
    row = conn.execute("SELECT current_database(), current_user").fetchone()
    print("연결 성공:", row)
