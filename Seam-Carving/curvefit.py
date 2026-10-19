import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

# Define the points to fit
naive_xs = np.array([10, 50, 100, 500, 1000])
naive_ys = np.array([0.0013814926147461, 0.021078586578369, 0.087698173522949, 6.9353436946869, 69.569059181213])

dynamic_xs = np.array([10, 50, 100, 500, 1000, 2400, 6100])
dynamic_ys = np.array([0.00049777030944824, 0.0097134590148926, 0.038419580459595, 0.926438331604, 4.050124835968, 27.10186214447, 88.469311])

# Fit both datasets
naive_spline = UnivariateSpline(naive_xs, naive_ys, s=1)
dynamic_spline = UnivariateSpline(dynamic_xs, dynamic_ys, s=1)

# Smooth out values
naive_x_fit = np.linspace(min(naive_xs), max(naive_xs), 1000)
dynamic_x_fit = np.linspace(min(dynamic_xs), max(dynamic_xs), 1000)

# Plot the data
plt.plot(naive_xs, naive_ys, 'ro', label='Naive')
plt.plot(dynamic_xs, dynamic_ys, 'bo', label='Dynamic')
plt.plot(naive_x_fit, naive_spline(naive_x_fit), 'r--')
plt.plot(dynamic_x_fit, dynamic_spline(dynamic_x_fit), 'b--')
plt.xlabel('Input size')
plt.ylabel('Time (s)')
plt.legend()
plt.show()
