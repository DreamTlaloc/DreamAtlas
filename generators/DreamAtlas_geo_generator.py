import numpy as np

from DreamAtlas import *


# @njit(parallel=True, fastmath=True)
def _numba_init_height_map(height_map, height_list):

    for height, x, y in range(height_list):
        height_map[x, y] = height

    return height_map


# @njit(parallel=True, fastmath=True)
def _numba_flow_map(height_map, min_seeds, iterations=1000):

    ping_filled_map = np.zeros(height_map.shape, dtype=np.float32)
    ping_filled_map *= 300
    pong_filled_map = np.zeros(height_map.shape, dtype=np.float32)

    flow_map = np.zeros((height_map.shape[0], height_map.shape[1], 2), dtype=np.int32)

    for h, x, y, in min_seeds:
        ping_filled_map[x, y] = height_map[x, y]

    neighbours = np.array([[1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [0, -1], [-1, -1], [-1, 0]], dtype=np.int32)

    # Fill all the depressions
    for _ in range(iterations):
        for x in prange(height_map.shape[0]):
            for y in prange(height_map.shape[1]):
                lowest = np.inf
                for n in neighbours:
                    x_n = x + n[0]
                    y_n = y + n[1]

                    x_v = x_n % height_map.shape[0]
                    y_v = y_n % height_map.shape[1]

                    if ping_filled_map[x, y] > ping_filled_map[x_v, y_v] and ping_filled_map[x_v, y_v] < lowest:
                        lowest = ping_filled_map[x_v, y_v]
                        flow = n

                if lowest == np.inf:
                    continue

                pong_filled_map[x, y] = max(height_map[x, y], lowest)
                flow_map[x, y] = flow

        if np.sum(ping_filled_map - pong_filled_map) < 0.1:
            break
        pong_filled_map = ping_filled_map

    return flow_map, pong_filled_map


def generator_geography(map_class, seed=None):

    height_maps = list()
    pixel_maps = list()

    # Generate the initial height map
    for plane in map_class.planes:
        height_map = np.zeros(map_class.map_size[plane], dtype=np.float32)
        height_list = np.array((len(map_class.province_list[plane]), 3), dtype=np.float32)

        for i, province in enumerate(map_class.province_list[plane]):  # Making the initial height map from the province heights
            height_list[i] = np.array((province.height, province.coordinates[0], province.coordinates[1]))

        height_map = _numba_init_height_map(height_map, height_list)

        # Add noise

        # Find the flow map
        flow_map, filled_map = _numba_flow_map(height_map, min_seeds, iterations=1000)

        height_maps[plane] = height_map
        pixel_maps[plane] = find_pixel_ownership(map_class.layout.province_graphs[plane].coordinates, map_class.map_size[plane], shapes, hwrap=True, vwrap=True, scale_down=8)

    return height_maps, pixel_maps


def plot_geography(height_map):

    fig, axs = plt.subplots(subplot_kw={'projection': '3d'})

    X, Y = np.meshgrid(np.arange(height_map.shape[1]), np.arange(height_map.shape[0]))
    axs[i].surface(X, Y, height_map, cmap='terrain', edgecolor='none')

    axs[i].axis('off')
