import re
with open(r"C:\Users\parsi\pp2\lab5\raw.txt","r", encoding="utf-8") as file:
    content=file.read()
if re.findall(r"\bБанковская карта\b",content):
    print("Банковская карта")
else:
    print("Наличными")
