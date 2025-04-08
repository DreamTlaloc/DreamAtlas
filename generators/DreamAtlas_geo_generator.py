from DreamAtlas import *


# @njit(parallel=True, fastmath=True)
def _numba_init_height_map(height_map, height_list):

    for height, x, y in range(height_list):
        height_map[x, y] = height

    return height_map



# @njit(parallel=True, fastmath=True)
def _numba_fill_depressions(height_map, iterations=100):

    flow_map = np.ones(height_map.shape, dtype=np.float32)
    flow_map *= 300

    # Fill all the depressions
    for _ in range(iterations):
        for x in prange(height_map.shape[0]):
            for y in prange(height_map.shape[1]):



    return flow_map


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

        # Fill the depressions in the height map
        flow_map = _numba_fill_depressions(height_map, iterations=100)

        height_maps[plane] = height_map
        pixel_maps[plane] = find_pixel_ownership(map_class.layout.province_graphs[plane].coordinates, map_class.map_size[plane], shapes, hwrap=True, vwrap=True, scale_down=8)

    return height_maps, pixel_maps


def plot_geography(height_map):

    fig, axs = plt.subplots(subplot_kw={'projection': '3d'})

    X, Y = np.meshgrid(np.arange(height_map.shape[1]), np.arange(height_map.shape[0]))
    axs[i].surface(X, Y, height_map, cmap='terrain', edgecolor='none')

    axs[i].axis('off')
