import numpy as np

BOUNDS = np.float32([[-0.3, 0.3], [-0.8, -0.2], [0, 0.15]])  # X Y Z



for i in range(10):
    rand_x = np.random.uniform(BOUNDS[0, 0] + 0.1, BOUNDS[0, 1] - 0.1)
    rand_y = np.random.uniform(BOUNDS[1, 0] + 0.1, BOUNDS[1, 1] - 0.1)
    rand_xyz = np.float32([rand_x, rand_y, 0.03]).reshape(1, 3)
    print(rand_xyz.squeeze())