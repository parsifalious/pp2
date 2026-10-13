import os
file_to_delete = "destination.txt"
if os.path.exists(file_to_delete) and os.access(file_to_delete, os.W_OK):
    os.remove(file_to_delete)
