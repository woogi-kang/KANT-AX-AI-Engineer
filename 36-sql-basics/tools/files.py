"""The SQL lines the deck types (demo.py runs them, gen.py shows them). Each list item is one line typed after the
psql prompt; a statement that runs over several lines gets the cafe-# style continuation prompt."""

TABLE = ["CREATE TABLE product (",
         "    id INTEGER PRIMARY KEY,",
         "    name VARCHAR(100),",
         "    category VARCHAR(20),",
         "    price INTEGER,",
         "    stock INTEGER",
         ");"]

PRODUCTS = [(1, "무선 이어폰", "audio", 35000, 100),
            (2, "게이밍 마우스", "input", 28000, 85),
            (3, "27인치 모니터", "display", 259000, 15),
            (4, "USB-C 허브", "acc", 19900, 200),
            (5, "노트북 거치대", "acc", 24000, 7),
            (6, "기계식 키보드", "input", 89000, 30),
            (7, "블루투스 스피커", "audio", 45000, 0),
            (8, "웹캠", "display", 52000, 12)]

ROWS = ["INSERT INTO product (id, name, category, price, stock) VALUES"] + [
    f"({i}, '{n}', '{c}', {p}, {s})" + ("," if k < len(PRODUCTS) - 1 else ";") for k, (i, n, c, p, s) in enumerate(PRODUCTS)]

MEMBER = ["CREATE TABLE member (",
          "    id INTEGER PRIMARY KEY,",
          "    name VARCHAR(20),",
          "    email TEXT,",
          "    grade VARCHAR(10),",
          "    points INTEGER,",
          "    joined DATE,",
          "    phone VARCHAR(13),",
          "    region VARCHAR(10)",
          ");"]

MEMBERS = [(1, "김하늘", "kim@gmail.com", "silver", 42000, "2026-09-03", "010-1234-5678", "마포구"),
           (2, "이도윤", "lee@naver.com", "basic", 8000, "2026-10-05", None, "강남구"),
           (3, "박서연", "park@gmail.com", "basic", 31500, "2026-10-12", "010-2222-3333", "마포구"),
           (4, "최지우", "choi@naver.com", "basic", 0, "2026-10-20", None, "송파구"),
           (5, "정우진", "jung@Gmail.com", "gold", 57000, "2026-08-14", "010-9876-5432", "강남구"),
           (6, "강민서", "kang@daum.net", "basic", 12000, "2026-11-02", None, "마포구")]


def _v(x):
    return "NULL" if x is None else (str(x) if isinstance(x, int) else f"'{x}'")


MEMBER_ROWS = ["INSERT INTO member VALUES"] + [
    "(" + ", ".join(_v(x) for x in m) + ")" + ("," if k < len(MEMBERS) - 1 else ";") for k, m in enumerate(MEMBERS)]
