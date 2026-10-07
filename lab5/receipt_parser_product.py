import re
with open(r"C:\Users\parsi\pp2\lab5\raw.txt","r", encoding="utf-8") as file:
    content=file.read()
product=re.findall(r"^\d{1,2}\.\s*\n([\s\S]*?)(?=\n\d+,\d{3}\s*x)",content,flags=re.MULTILINE)
for i in product:
    print(i)