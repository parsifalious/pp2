names = ["Anna", "Bob"]
scores = [90, 85]
for i, name in enumerate(names):
    print(i, name)
for name, score in zip(names, scores):
    print(name, score)
