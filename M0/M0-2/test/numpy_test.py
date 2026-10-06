import numpy as np

data = np.genfromtxt(
    'sample_data.csv',
    delimiter=',',
    names=True,
    dtype=float,
    encoding='utf-8'
)

x = data['sensor_a']
y = data['sensor_b']

r = np.corrcoef(x, y)[0, 1]
print(r)