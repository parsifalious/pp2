N=int(input("Введите число: "))
sqr=(i**2 for i in range(1,N+1))
for num in sqr:
    print(num)