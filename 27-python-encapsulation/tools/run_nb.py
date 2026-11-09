"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback."""
import re

import nbclient
import nbformat


def run(cells, timeout=None):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
    kw = dict(timeout=timeout, interrupt_on_timeout=True) if timeout else {}
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True, **kw).execute()
    for c in nb.cells:
        print(f"--- [{c.execution_count}] {c.source!r}")
        for o in c.outputs:
            if o.output_type == "error":
                last = re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(o.traceback)).strip().splitlines()[-1]
                print(last)   # last traceback line, with hints like "Did you mean"
            else:
                t = o.get("text") or o.get("data", {}).get("text/plain")
                lines = t.splitlines()
                if len(lines) > 12:
                    t = "\n".join(lines[:5]) + f"\n... ({len(lines)} lines)"
                print(t)



C0 = '''class Card:
    def __init__(self, name):
        self.name = name
        self.stamps = 0

    def add(self):
        self.stamps = self.stamps + 1
'''

print("=== 1. 왜 필요한가")
run([C0 + '''
kim = Card("kim")
kim.add()
kim.stamps = 100
print(kim.name, kim.stamps)''',
     '''kim.stamps = -5
print(kim.name, kim.stamps)'''])

print("=== 2. 밑줄 하나")
run(['''class Card:
    def __init__(self, name):
        self.name = name
        self._stamps = 0

    def add(self):
        self._stamps = self._stamps + 1

    def count(self):
        return self._stamps

kim = Card("kim")
kim.add()
kim.add()
print(kim.count())''',
     '''kim._stamps = 100
print(kim.count())'''])

S1 = '''class Secret:
    def __init__(self):
        self.__password = 1234
'''
print("=== 3. 밑줄 두 개")
run([S1 + '''
mypass = Secret()
print(mypass.__password)''',
     '''class Secret:
    def __init__(self):
        self.__password = 1234

    def check(self, pw):
        return self.__password == pw

mypass = Secret()
print(mypass.check(1234))
print(mypass.check(1111))''',
     '''print(mypass.__dict__)''',
     '''print(mypass._Secret__password)''',
     '''mypass._Secret__password = 5678
print(mypass.check(5678))'''])

print("=== 눌러 보기 (이름 바꾸기)")
for inside in ["password", "_password", "__password"]:
    cells = [f'''class Secret:
    def __init__(self):
        self.{inside} = 1234

mypass = Secret()
print(mypass.__dict__)''']
    for outside in ["password", "_password", "__password", "_Secret__password"]:
        cells.append(f"print(mypass.{outside})")
    run(cells)

GS = '''class Secret:
    def __init__(self):
        self.__password = 1234

    def get_password(self):
        return self.__password

    def set_password(self, new):
        if 1000 <= new <= 9999:
            self.__password = new
        else:
            print("비밀번호는 네 자리 숫자예요")
'''
print("=== 4. getter와 setter")
run([GS + '''
mypass = Secret()
print(mypass.get_password())''',
     '''mypass.set_password(12)
print(mypass.get_password())
mypass.set_password(5678)
print(mypass.get_password())''',
     '''class Secret:
    def __init__(self):
        self.__password = 1234

    @property
    def password(self):
        return self.__password

mypass = Secret()
print(mypass.password)''',
     '''class Secret:
    def __init__(self):
        self.__password = 1234

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, new):
        if 1000 <= new <= 9999:
            self.__password = new
        else:
            print("비밀번호는 네 자리 숫자예요")

mypass = Secret()
mypass.password = 12
print(mypass.password)
mypass.password = 5678
print(mypass.password)'''])

print("=== 4. (비교) 검사 없이 바로 넣기")
run(['''class Secret:
    def __init__(self):
        self.password = 1234

mypass = Secret()
mypass.password = 12
print(mypass.password)'''])

print("=== 5. 오류와 함정")
run(['''class Secret:
    def __init__(self):
        self.__password = 1234

    def check(self, pw):
        return self.__password == pw

mypass = Secret()
mypass.__password = 0
print(mypass.check(1234))
print(mypass.__dict__)''',
     '''class Card:
    def __init__(self, name):
        self.name = name
        self.__stamps = 0

    def add(self):
        self.__stamps = self.__stamps + 1

class VipCard(Card):
    def add(self):
        self.__stamps = self.__stamps + 2

lee = VipCard("lee")
lee.add()''',
     '''class Card:
    def __init__(self, name):
        self.name = name
        self.__stamps = 0

    @property
    def stamps(self):
        return self.__stamps

kim = Card("kim")
print(kim.stamps())''',
     '''kim.stamps = 100''',
     '''class Card:
    def __init__(self, name):
        self.name = name
        self._stamps = 0

    def add(self):
        self._stamps = self._stamps + 1

class VipCard(Card):
    def add(self):
        self._stamps = self._stamps + 2

lee = VipCard("lee")
lee.add()
print(lee._stamps)'''])

print("=== 6. 실습")
run(['''class Card:
    goal = 10

    def __init__(self, name):
        self.name = name
        self.__stamps = 0

    def add(self):
        if self.__stamps < Card.goal:
            self.__stamps = self.__stamps + 1

    @property
    def stamps(self):
        return self.__stamps

    def __str__(self):
        return f"{self.name}: 도장 {self.__stamps}/{Card.goal}"''',
     '''kim = Card("kim")
for i in range(12):
    kim.add()
print(kim)
print(kim.stamps)''',
     '''class Kiosk:
    def __init__(self, password):
        self.__password = password

    def login(self, pw):
        if pw == self.__password:
            print("관리자 화면을 열어요")
        else:
            print("비밀번호가 틀렸어요")

    def change(self, old, new):
        if old == self.__password:
            self.__password = new
            print("비밀번호를 바꿨어요")
        else:
            print("지금 비밀번호가 틀려서 못 바꿔요")''',
     '''k = Kiosk(1234)
k.login(1111)
k.change(1111, 5678)
k.change(1234, 5678)
k.login(5678)'''])
