def fahrenheit_to_celsius(f):
    return (5/9) * (f - 32)

f = float(input("Введите температуру: "))
print(fahrenheit_to_celsius(f))