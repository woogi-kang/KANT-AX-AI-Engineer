fees = [70000, 70000, 80000, 90000, 60000, 120000, 100000, 65000, 75000, 90000, 110000, 130000, 150000, 160000]
avg = sum(fees) / len(fees)
print(avg)
print([f for f in fees if f > avg])
