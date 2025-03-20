from DreamAtlas import *


def _numba_fill_depressions(height_map, iterations=100):

    flow_map = np.ones(height_map.shape, dtype=np.float32)
    flow_map *= 300

    # Fill all the depressions
    for _ in range(iterations):
        for x in prange(height_map.shape[0]):
            for y in prange(height_map.shape[1]):



    return flow_map


def generator_geography(map_class, seed=None):

    # Generate the initial height map
    for plane in map_class.planes:
        pixel_map = find_pixel_ownership(map_class.layout.province_graphs[plane].coordinates, map_class.map_size[plane], shapes, hwrap=True, vwrap=True, scale_down=8)
        height_map = np.zeros(map_class.map_size[plane], dtype=np.float32)

        for province in map_class.province_list[plane]:
            pass

        pixel_map = np.zeros(map_class.map_size[plane], dtype=np.int32)
        pixel_owner_list = list()


    return height_maps, pixel_maps, pixel_owner_lists

