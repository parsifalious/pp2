import os
path = "."
print(os.listdir(path))
print([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
print([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
