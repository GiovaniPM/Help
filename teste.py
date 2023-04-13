import math

def newton(a, b, epsilon):
    while (b - a) / 2 > epsilon:
        c = (a + b) / 2
        fa = f(a)
        fb = f(b)
        fc = f(c)
        if fc == 0:
            break
        elif fa * fc < 0:
            b = c
        else:
            a = c
    return (a + b) / 2

def f(x):
    return x**2 - x*5 + 6

print("A solução aproximada é: ", newton(-50, 50, 0.0001))

def f(x):
    return x**2 - x*2 - 10

print("A solução aproximada é: ", newton(-5, 5, 0.0001))

def f(x):
    return x**4 + x**2 - 174

print("A solução aproximada é: ", newton(-500000000, 500000000, 0.0001))

def f(x):
    return x**3 + x*2 - 174

print("A solução aproximada é: ", newton(-500000000, 500000000, 0.0001))