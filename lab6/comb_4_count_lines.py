target = "sample.txt"
with open(target, "r") as f:
    print(sum(1 for _ in f))
