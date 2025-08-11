from DreamAtlas import *


def make_noise_array(map_size, scale):
    x_size, y_size = map_size
    noise_array = np.zeros((x_size, y_size, 2), dtype=np.float32)

    base_x, base_y = np.random.randint(1, 10000, size=2, dtype=np.int32)

    for x in range(map_size[0]):
        for y in range(map_size[1]):
            vx, vy = x/x_size, y/y_size

            noise_array[x, y, 0] = ns.snoise2(vx, vy, octaves=7, persistence=0.90, lacunarity=2.0, repeatx=1, repeaty=1, base=base_x)
            noise_array[x, y, 1] = ns.snoise2(vx, vy, octaves=7, persistence=0.90, lacunarity=2.0, repeatx=1, repeaty=1, base=base_y)

    return noise_array * scale


@njit(parallel=True, cache=True, fastmath=True)
def cleanup_isolated_pixels(pixel_map):

    output_pixel_map = pixel_map
    shape_x, shape_y = np.shape(pixel_map)

    for iteration in range(5):
        for x in prange(shape_x):
            for y in prange(shape_y):

                isolated = 0

                for n in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
                    vx, vy = x + n[0], y + n[1]
                    vx, vy = vx % shape_x, vy % shape_y

                    if pixel_map[vx, vy] == pixel_map[x, y]:
                        isolated += 1

                if isolated <= 1:
                    output_pixel_map[x, y] = pixel_map[vx, vy]

    return output_pixel_map


def simplex_generator_geography(map_class, seed=None):

    if seed is None:
        seed = np.random.randint(1, 1000000)
    np.random.seed(seed)

    height_maps = [None for _ in range(10)]
    pixel_maps = [None for _ in range(10)]

    # Generate the initial height map
    for plane in map_class.planes:

        height_array = np.zeros(len(map_class.province_list[plane])+1, dtype=np.int16)
        for province in map_class.province_list[plane]:
            height_array[province.index] = terrain_2_height(province.terrain_int)

        noise_array = make_noise_array(map_class.map_size[plane], 150)

        pixel_maps[plane] = find_pixel_ownership(map_class.layout.province_graphs[plane].coordinates, map_class.map_size[plane], noise_array,  scale_down=4)
        height_maps[plane] = numba_height_map(pixel_maps[plane], height_array)
        # pixel_maps[plane] = cleanup_isolated_pixels(pixel_maps[plane])

    return height_maps, pixel_maps
