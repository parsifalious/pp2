import re
text=input()
capital=re.sub(r"(?=[A-Z])"," ",text)
print(capital.strip())