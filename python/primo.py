from threading import Thread
import time

def ehPrimo(number: int):
    i = 3
    ii = 1
    
    if number == 0:
        return False, ii, 0
    elif number == 1:
        return True, ii, 1
    elif number == 2:
        return True, ii, 2
    elif number == 3:
        return True, ii, 3
    elif number == 5:
        return True, ii, 5
    elif number % 2 == 0:
        return False, ii, 2
    elif number % 5 == 0:
        return False, ii, 5
    elif number > 2:
        while i < ((number + 1 )/ 2):
            if number % i == 0:
                return False, ii, i
            i = i + 2
            if (i % 5 == 0) and (i % 2 != 0):
                i = i + 2
            ii += 1
        else:
            return True, ii, number
    else:
        return False, ii, number

def geraPrimos(number: int):
    vector = [1, 2, 3, 5, 7]
    
    x = 8
    while x <= number:
        i = len(vector)
        y = 1
        primo = True
        while y < (i / 2):
            if x % vector[y] == 0:
                primo = False
                break
            y += 1
        if primo:
            vector.append(x)
        x += 1
    return vector

def geraPrimosT(number: int):
    def task(valor):
        i = len(vector)
        y = 1
        primo = True
        while y < (i / 2):
            if valor % vector[y] == 0:
                primo = False
                break
            y += 1
        if primo:
            vector.append(x)
    
    vector = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    x = 100
    while x <= number:
        threads = []
        
        for n in range(1, 5):
            t = Thread(target=task, args=(x,))
            threads.append(t)
            t.start()
            x += 1

        for t in threads:
            t.join()

    return vector

start_1 = time.time()
primos = []

for x in range(1,100000):
    Eh, iteracoes, valor = ehPrimo(x)
    if Eh:
        primos.append(x)

print(primos)
end_1 = time.time()

start_2 = time.time()
print(geraPrimos(100000))
end_2 = time.time()

start_3 = time.time()
print(geraPrimosT(100000))
end_3 = time.time()

print("um", end_1 - start_1)
print("dois", end_2 - start_2)
print("tres", end_3 - start_3)