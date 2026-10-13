N=int(input("Введите число: "))
Even=(i for i in range (N+1))
for num in Even:
    if num%2==0:
        print(num)