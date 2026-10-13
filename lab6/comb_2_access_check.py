import os
target = "sample.txt"
print(os.path.exists(target))
print(os.access(target, os.R_OK))
print(os.access(target, os.W_OK))
print(os.access(target, os.X_OK))
