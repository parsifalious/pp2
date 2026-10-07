import re
text=input()
if re.fullmatch(r"^a.*b$",text):
    print("matches")
else:
    print("no match")