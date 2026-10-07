import re
text=input()
x=re.sub(r"[\s,.]+",":",text)
print(x)