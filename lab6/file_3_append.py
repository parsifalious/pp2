with open("sample.txt", "a", encoding="utf-8") as f:
    f.write("\nNew line")
with open("sample.txt", "r", encoding="utf-8") as f:
    print(f.read())
