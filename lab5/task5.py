import re
text=input()
if re.fullmatch(r"a.*b",text):
    print("match")
else:
    print("not matches")