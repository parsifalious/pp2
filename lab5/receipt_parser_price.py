import re
with open(r"C:\Users\parsi\pp2\lab5\raw.txt","r", encoding="utf-8") as file:
    content=file.read()
price=re.findall(r"Стоимость\s*\n\s*(\d{1,3}(?:\s?\d{3})?,00)",content)

for x in price:
    print(x)