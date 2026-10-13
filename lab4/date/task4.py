from datetime import datetime

d1 = datetime.strptime(input("Первая дата (ДД.ММ.ГГГГ): "), "%d.%m.%Y")
d2 = datetime.strptime(input("Вторая дата (ДД.ММ.ГГГГ): "), "%d.%m.%Y")

print("Разница в секундах:", (d2 - d1).total_seconds())