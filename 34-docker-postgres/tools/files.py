"""The files the student writes in ~/cafe-pg. demo.py writes them for real, gen.py shows the same text."""
COMPOSE = '''services:
  pg:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: cafe1234
      POSTGRES_DB: cafe
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql

volumes:
  pg-data:
'''
COMPOSE_INIT = COMPOSE.replace("      - pg-data:/var/lib/postgresql\n", "      - pg-data:/var/lib/postgresql\n      - ./init:/docker-entrypoint-initdb.d\n")
MENU_SQL = '''CREATE TABLE menu (id INT PRIMARY KEY, name VARCHAR(20), price INT);
INSERT INTO menu VALUES (1, 'americano', 4000);
INSERT INTO menu VALUES (2, 'latte', 4500);
INSERT INTO menu VALUES (3, 'cake', 5000);
'''
