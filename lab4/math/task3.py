import math
side=int(input("Введите количество сторон: "))
length=int(input("Введите длину: "))
S=(side*(length**2))/(4*math.tan(math.pi / side))
print(int(S))