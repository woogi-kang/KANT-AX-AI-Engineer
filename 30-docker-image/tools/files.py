"""The files the deck shows and tools/demo.py writes into the student's folders."""

SITE1 = '''<meta charset="utf-8">
<h1>KANT 카페 메뉴</h1>
<p>아메리카노 4,500원</p>
'''
SITE2 = SITE1 + '<p>카페라테 5,000원</p>\n'
COMPOSE = '''services:
  web:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./site:/usr/share/nginx/html
'''
DOCKERFILE = '''FROM astral/uv:python3.14-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync
CMD ["uv", "run", "main.py"]
'''
DOCKERIGNORE = '''.venv
__pycache__
.git
'''
