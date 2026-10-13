import re
sum=0
with open(r"C:\Users\parsi\pp2\lab5\raw.txt","r", encoding="utf-8") as file:
    content=file.read()
print()
txt=("SHORT RECEIPT")
print(txt.center(20))
print("="*20)
date=re.findall(r"\b\d{2}\.\d{2}\.\d{4}",content)
for x in date:
    print("DATE:",x)
time=re.findall(r"\b\d{2}:\d{2}:\d{2}",content)
for x in time:
    print("TIME:",x)
price=re.findall(r"Стоимость\s*\n\s*(\d{1,3}(?:\s?\d{3})?,00)",content)
for x in price:
    x=x.replace(" ","")
    x=x.replace(",",".")
    sum+=(float(x))
print("TOTAL:",sum)
product=re.findall(r"^\d{1,2}\.\s*\n([\s\S]*?)(?=\n\d+,\d{3}\s*x)",content,flags=re.MULTILINE)
products_count=len(product)
print("PRODUCTS COUNT:",products_count)
print("="*20)
if re.findall(r"\bБанковская карта\b",content):
    print("PAYMENT METHOD: CARD")
else:
    print("PAYMENT METHOD: CASH")
print()
