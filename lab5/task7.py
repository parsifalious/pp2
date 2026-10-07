import re
text=input()
words = re.split(r"_", text)
result = words[0] + "".join(w.capitalize() for w in words[1:])
print(result)