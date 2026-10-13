my_list = ["Первая строка\n", "Вторая строка\n"]
with open("list_file.txt", "w") as f:
    f.writelines(my_list)
