with open("sample.txt", "r") as src, open("destination.txt", "w") as dst:
    dst.write(src.read())
