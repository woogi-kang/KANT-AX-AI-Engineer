import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

conn = psycopg.connect(DSN)
conn.execute("UPDATE members SET phone = '010-1111-2222' WHERE member_id = 10")
conn.commit()
print("바꿨어요")
conn.close()
