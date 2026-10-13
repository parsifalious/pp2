import os
target = "sample.txt"
if os.path.exists(target):
    print(os.path.dirname(os.path.abspath(target)))
    print(os.path.basename(os.path.abspath(target)))
