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



A = '''class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name}가 밥을 먹어요")

    def speak(self):
        print(f"{self.name}가 소리를 내요")
'''

print("=== 1. 왜 필요한가")
run(['''class Dog:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name}가 밥을 먹어요")

    def speak(self):
        print(f"{self.name}가 멍멍 짖어요")

d = Dog("초코")
d.speak()''',
     '''class Cat:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name}가 밥을 먹어요")

    def speak(self):
        print(f"{self.name}가 야옹 울어요")

c = Cat("나비")
c.speak()'''])

print("=== 2. 클래스 변수")
run(['''class Bread:
    shop = "붕어빵 1호점"

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a.shop)
print(b.shop)
print(Bread.shop)''',
     '''Bread.shop = "붕어빵 2호점"
print(a.shop)
print(b.shop)''',
     '''class Bread:
    count = 0

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        Bread.count = Bread.count + 1

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
c = Bread("피자", 1500)
print(Bread.count)'''])

print("=== 3. 상속")
run([A,
     '''class Dog(Animal):
    pass

d = Dog("초코")
d.eat()
d.speak()''',
     '''class Dog(Animal):
    def fetch(self):
        print(f"{self.name}가 공을 물어 와요")

a = Animal("하마")
d = Dog("초코")
d.eat()
d.fetch()''',
     '''a.fetch()''',
     '''class Dog(Animal):
    def speak(self):
        print(f"{self.name}가 멍멍 짖어요")

d = Dog("초코")
d.speak()''',
     '''class Cat(Animal):
    def speak(self):
        print(f"{self.name}가 야옹 울어요")

c = Cat("나비")
c.speak()''',
     '''a.speak()''',
     '''class Dog(Animal):
    def eat(self):
        super().eat()
        print(f"{self.name}가 꼬리를 흔들어요")

d = Dog("초코")
d.eat()''',
     '''class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        print(f"{self.name}가 멍멍 짖어요")

d = Dog("초코", "푸들")
print(d.name, d.breed)
d.speak()''',
     '''animals = [Dog("초코", "푸들"), Cat("나비"), Animal("하마")]
for x in animals:
    x.speak()''',
     '''print(isinstance(d, Dog))
print(isinstance(d, Animal))
print(isinstance(a, Dog))'''])

print("=== 5. 오류와 함정 (4파트 비교는 셀 없음)")
run([A + '''
class Dog(Animal):
    def __init__(self, name, breed):
        self.breed = breed

d = Dog("초코", "푸들")
d.eat()''',
     '''class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(self, name)
        self.breed = breed

d = Dog("초코", "푸들")''',
     '''class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

d = Dog("초코")''',
     '''class Bread:
    shop = "붕어빵 1호점"

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
a.shop = "옆 가게"
print(a.shop)
print(b.shop)
print(Bread.shop)''',
     '''class Bread:
    count = 0

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        self.count = self.count + 1

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a.count, b.count)
print(Bread.count)''',
     '''class Dog(Anmal):
    pass'''])

print("=== 6. 실습")
run(['''class Card:
    shop = "KANT 카페"
    goal = 10

    def __init__(self, name):
        self.name = name
        self.stamps = 0

    def add(self):
        self.stamps = self.stamps + 1

    def __str__(self):
        left = Card.goal - self.stamps
        return f"[{Card.shop}] {self.name}: 도장 {self.stamps}개, {left}개 남음"

class VipCard(Card):
    def add(self):
        self.stamps = self.stamps + 2''',
     '''kim = Card("kim")
lee = VipCard("lee")
kim.add()
kim.add()
lee.add()
lee.add()
print(kim)
print(lee)''',
     '''class Bread:
    count = 0

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        Bread.count = Bread.count + 1

    def __str__(self):
        return f"{self.flavor} 붕어빵 {self.price:,}원"

class MiniBread(Bread):
    def __init__(self, flavor, price, qty):
        super().__init__(flavor, price)
        self.qty = qty

    def __str__(self):
        return f"미니 {self.flavor} {self.qty}개 {self.price * self.qty:,}원"''',
     '''menu = [Bread("팥", 1000), MiniBread("팥", 300, 5), Bread("슈크림", 1200), MiniBread("슈크림", 400, 5)]
for m in menu:
    print(m)
print("찍은 붕어빵:", Bread.count)
print([m.flavor for m in menu if isinstance(m, MiniBread)])'''])

print("=== 눌러 보기 (메서드 찾기 장의 출력)")
run(['''class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name}가 밥을 먹어요")

    def speak(self):
        print(f"{self.name}가 소리를 내요")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        print(f"{self.name}가 멍멍 짖어요")

    def fetch(self):
        print(f"{self.name}가 공을 물어 와요")

a = Animal("하마")
d = Dog("초코", "푸들")''',
     '''a.speak()''',
     '''d.speak()''',
     '''a.eat()''',
     '''d.eat()''',
     '''a.fetch()''',
     '''d.fetch()''',
     '''print(a.breed)''',
     '''print(d.breed)''',
     '''print(a.name)''',
     '''print(d.name)'''])
