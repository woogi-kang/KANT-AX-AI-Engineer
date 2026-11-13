"""The files the student has in ~/kant-shop. demo.py writes them for real, gen.py shows the same text.
kant_shop.sql is the class file (IndieGameMaker/kant_docker) as it is. compose.yaml follows the class format
(services, image, container_name, environment, ports, volumes, top-level volumes)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SQL = open(os.path.join(HERE, "kant_shop.sql"), encoding="utf-8").read()

COMPOSE = '''services:
  db:
    image: postgres:18
    container_name: my-pg
    environment:
      POSTGRES_PASSWORD: admin1234
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql

volumes:
  pgdata:
'''
# the same file without container_name: compose makes the name from the folder and the service
COMPOSE_NONAME = COMPOSE.replace("    container_name: my-pg\n", "")
# the same file indented by four spaces
COMPOSE_FOUR = "\n".join(" " * (2 * (len(l) - len(l.lstrip(" ")))) + l.lstrip(" ") for l in COMPOSE.split("\n"))
# broken files for the error slides
COMPOSE_TAB = COMPOSE.replace("    image: postgres:18\n", "\timage: postgres:18\n")
COMPOSE_MIX = COMPOSE.replace("    container_name: my-pg\n", "  container_name: my-pg\n")
COMPOSE_COLON = COMPOSE.replace("    image: postgres:18\n", "    image:postgres:18\n")
