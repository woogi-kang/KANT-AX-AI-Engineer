"""The files the student writes in ~/cafe-db. demo.py writes them for real, gen.py shows the same text."""
COMPOSE = '''services:
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: cafe1234
      MYSQL_DATABASE: cafe
    ports:
      - "3306:3306"
    volumes:
      - cafe-data:/var/lib/mysql

volumes:
  cafe-data:
'''
COMPOSE_INIT = COMPOSE.replace("      - cafe-data:/var/lib/mysql\n", "      - cafe-data:/var/lib/mysql\n      - ./init:/docker-entrypoint-initdb.d\n")
MENU_SQL = '''CREATE TABLE menu (id INT PRIMARY KEY, name VARCHAR(20), price INT);
INSERT INTO menu VALUES (1, 'americano', 4000);
INSERT INTO menu VALUES (2, 'latte', 4500);
INSERT INTO menu VALUES (3, 'cake', 5000);
'''
