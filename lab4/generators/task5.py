N=int(input("Введите число: "))
reverse=(i for i in range(N,-1,-1))
for num in reverse:
    print(num,end=",")