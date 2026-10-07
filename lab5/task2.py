import re
text=input()
if re.fullmatch(r"^ab{2,3}$",text):
    print("matches")
else:
    print("no match")