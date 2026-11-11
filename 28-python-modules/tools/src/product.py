class Product:
    next_id = 1 # 클래스 변수

    # 새 상품의 초기 정보 저장
    def __init__(self, name, price, stock):
        self.id = Product.next_id
        Product.next_id += 1 # 다음 상품을 위해 Index 값 +1
        self.name = name
        self.price = price
        self.stock = stock

    def is_sold_out(self):
        return self.stock == 0

    def __str__(self):
        stock_text = "품절" if self.is_sold_out() else f"재고 {self.stock}개"
        return f"{self.id}: {self.name:<10} {self.price:>8,} {stock_text}"



# -------------------------------------------
# 테스트 코드
# -------------------------------------------
# 이 파일을 직접 실행 시켰을 만 코드가 실행 되도록 하는 로직
# uv run product.py
if __name__ == "__main__":
    products = [
        Product("무선 이어폰", 89_000, 3),
        Product("텀블러", 15_000, 10),
        Product("보조베터리", 32_000, 5),
        Product("마우스패드", 9_000, 0),
        Product("USB 허브", 30_000, 10),
    ]

    for p in products: print(p)
