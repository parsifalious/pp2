import os
import shutil
os.makedirs("dir1", exist_ok=True)
os.makedirs("dir2", exist_ok=True)
open("dir1/file.txt", "w").close()
shutil.move("dir1/file.txt", "dir2/file.txt")
