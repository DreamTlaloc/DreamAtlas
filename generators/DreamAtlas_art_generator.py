from DreamAtlas import *


def generator_art(map_class, seed=None):

    """
    Generates the art for the map
    """
    # Generate the initial height map
    for plane in map_class.planes:
        pixel_map = find_pixel_ownership(map_class.layout.province_graphs[plane].coordinates, map_class.map_size[plane], shapes, hwrap=True, vwrap=True, scale_down=8)
        height_map = np.zeros(map_class.map_size[plane], dtype=np.float32)

        for province in map_class.province_list[plane]:
            pass

        pixel_map = np.zeros(map_class.map_size[plane], dtype=np.int32)
        pixel_owner_list = list()