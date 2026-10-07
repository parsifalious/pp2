import re
text=input()
if re.fullmatch(r"[A-Z][a-z]+",text):
    print("matches")
else:
    print("no match")
