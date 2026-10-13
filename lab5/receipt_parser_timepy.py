import re
with open(r"C:\Users\parsi\pp2\lab5\raw.txt","r", encoding="utf-8") as file:
    content=file.read()
time=re.findall(r"\b\d{2}\.\d{2}\.\d{4}\s\b\d{2}:\d{2}:\d{2}",content)
for x in time:
    print(x)