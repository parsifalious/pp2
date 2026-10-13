a,b = map(int, input("Введите число a и b: ").split())
def squares(a,b):
    for i in range (a,b+1):
        yield i**2

for x in squares(a,b):
    print (x,end=",")