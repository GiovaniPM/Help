import random

def estimate_pi(num_samples):
    inside_circle = 0
    
    for _ in range(num_samples):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x**2 + y**2 <= 1:
            inside_circle += 1
    
    return (inside_circle / num_samples) * 4

# Estimar π usando 1.000.000 amostras
print(estimate_pi(1000000))