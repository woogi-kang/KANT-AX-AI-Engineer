"""The files the deck shows and tools/demo.py writes into the student's ~/cafe folder."""

SITE = '''<meta charset="utf-8">
<h1>KANT 카페</h1>
<p><a href="/menu/">메뉴 보기</a></p>
<p><a href="/order/">주문하기</a></p>
'''
EVENT_HTML = '''<meta charset="utf-8">
<h1>이번 주 이벤트</h1>
'''

CONF_FILES = '''server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
'''

CONF_MENU = '''server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /menu/ {
        proxy_pass http://menu/;
    }
}
'''

CONF_BOTH = CONF_MENU.replace('''        proxy_pass http://menu/;
    }
''', '''        proxy_pass http://menu/;
    }

    location /order/ {
        proxy_pass http://order/;
    }
''')

CONF_EVENT = CONF_BOTH.replace('''        proxy_pass http://order/;
    }
''', '''        proxy_pass http://order/;
    }

    location /event/ {
        proxy_pass http://event/;
    }
''')

COMPOSE = '''services:
  web:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./site:/usr/share/nginx/html
      - ./conf:/etc/nginx/conf.d
    depends_on:
      - menu
      - order
  menu:
    image: traefik/whoami
    command: --name menu
  order:
    image: traefik/whoami
    command: --name order
'''

COMPOSE_EVENT = COMPOSE.replace("      - order\n", "      - order\n      - event\n", 1) + '''  event:
    image: traefik/whoami
    command: --name event
'''
