import re
text=input()
replaced_text=text.replace(" ","")
snaking=re.sub(r"(?<!^)(?=[A-Z])","_",replaced_text)
print(snaking.lower())