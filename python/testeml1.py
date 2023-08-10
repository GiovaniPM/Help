import tensorflow as tf
import numpy as np
from tensorflow import keras

model = keras.Sequential([keras.layers.Dense(units=1, input_shape=[1])])
model.compile(optimizer='sgd', loss='mean_squared_error')

#xs = np.array([-1.0, 0.0, 1.0, 2.0, 3.0, 4.0], dtype=float)
#ys = np.array([-3.0, -1.0, 1.0, 3.0, 5.0, 7.0], dtype=float)
#
#model.fit(xs, ys, epochs=500)
#
#print(model.predict([10.0]))
#print(model.predict([20.0]))
#print(model.predict([30.0]))

xs = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], dtype=float)
ys = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0], dtype=float)

model.fit(xs, ys, epochs=5000)

print(model.predict([10.0]))
print(model.predict([20.0]))
print(model.predict([30.0]))