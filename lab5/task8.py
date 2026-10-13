import re
text=input()
splitting =re.sub(r"(?=[A-Z])"," ",text).strip()
print(splitting.split())