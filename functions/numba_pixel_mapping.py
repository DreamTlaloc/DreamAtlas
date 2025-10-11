# Imports all the DreamAtlas functionality and dependencies
from DreamAtlas import *


@njit(fastmath=True, cache=True)
def minkowski(v, p, ip):
    return (abs(v[0]) ** p + abs(v[1]) ** p) ** ip


@njit(fastmath=True, cache=True)
def tlalocean(u, v):
    r1 = u[0] - v[0]
    r2 = u[1] - v[1]
    r3 = u[2] - v[2]
    return (2 - (np.sign(u[2]) * np.sign(v[2]))) * (r1 * r1 + r2 * r2 + r3 * r3) ** 0.5


@njit(fastmath=True, cache=True)
def euclidean_2d(v):
    return (v[0] * v[0] + v[1] * v[1]) ** 0.5


@njit(parallel=True, cache=True, fastmath=True)
def _jump_flood_algorithm(pixel_matrix: np.array,
                          noise_matrix: np.array,
                          step_size: int,
                          distance_matrix: np.array,
                          vector_matrix: np.array):

    shape_x, shape_y = np.shape(pixel_matrix)

    end = False
    ping_matrix = pixel_matrix
    pong_matrix = pixel_matrix
    ping_distance_matrix = distance_matrix
    pong_distance_matrix = distance_matrix
    ping_vector_matrix = vector_matrix
    pong_vector_matrix = vector_matrix

    counter = 0
    while True:
        step_size = int(0.5 + step_size / 2)
        neighbours = np.array([[step_size, -step_size], [step_size, 0], [step_size, step_size], [0, step_size],
                               [-step_size, step_size], [0, -step_size], [-step_size, -step_size], [-step_size, 0]],
                              dtype=np.int32)

        for x in prange(shape_x):
            for y in prange(shape_y):
                p = ping_matrix[x, y]
                for n in neighbours:

                    vx, vy = x + n[0], y + n[1]
                    rx, ry = vx % shape_x, vy % shape_y
                    q = ping_matrix[rx, ry]

                    # Main logic of the Jump Flood Algorithm (if the pixels are identical or q has no info go to next)
                    if p == q or q == 0:
                        continue
                    else:
                        q_vector = ping_vector_matrix[rx, ry] - n  # q_vector is the vector from the ping pixel to the q pixel
                        q_dist = euclidean_2d(q_vector - noise_matrix[x, y])  # q_dist is the distance from the ping pixel to the q pixel
                        if p == 0 or ping_distance_matrix[x, y] > q_dist:  # if our pixel is empty or closer to q, populate it with q
                            pong_distance_matrix[x, y] = q_dist
                            pong_vector_matrix[x, y] = q_vector
                            pong_matrix[x, y] = q

        ping_matrix = pong_matrix
        ping_distance_matrix = pong_distance_matrix
        ping_vector_matrix = pong_vector_matrix

        if end and step_size == 1:  # Breaking the while loop
            counter += 1
            if counter == 5:
                break
        if step_size == 1:  # Does a final pass
            step_size = 16
            end = True

    return ping_matrix, ping_distance_matrix, ping_vector_matrix


def find_pixel_ownership(coordinates_array: np.array,
                         map_size: np.array,
                         noise_array: np.array = np.array,
                         scale_down: int = 2):
    # Runs a jump flood algorithm on a scaled down version of the map, then scales up and redoes the algorithm more
    # finely. This speeds up runtime significantly. The main function of the JFA is run in Numba, which speeds up the
    # code and allows it to be run in parallel on CPU or GPU.

    small_x_size = int(map_size[0] / scale_down)
    small_y_size = int(map_size[1] / scale_down)
    small_matrix = np.zeros((small_x_size, small_y_size), dtype=np.uint16)

    s_distance_matrix = np.full((small_x_size, small_y_size), np.inf, dtype=np.float32)
    s_vector_matrix = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)
    small_noise_array = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)
    # small_noise_array = noise_array[::scale_down, ::scale_down, :] / scale_down

    for i, (x, y) in enumerate(coordinates_array):
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        small_matrix[x_small, y_small] = i+1
        s_distance_matrix[x_small, y_small] = 0

    small_output_matrix, small_distance_matrix, small_vector_matrix = _jump_flood_algorithm(small_matrix,
                                                                                            noise_matrix=small_noise_array,
                                                                                            step_size=2 ** (int(1 + np.log(max(map_size) / scale_down))),
                                                                                            distance_matrix=s_distance_matrix,
                                                                                            vector_matrix=s_vector_matrix)

    # Scale the matrix back up and run a JFA again to refine
    zoom = np.divide(map_size, small_output_matrix.shape)
    final_matrix = sc.ndimage.zoom(small_output_matrix, zoom=zoom, order=0, output=np.uint16)[:map_size[0], :map_size[1]]
    final_distance_matrix = sc.ndimage.zoom(small_distance_matrix * scale_down, zoom=zoom, order=0, output=np.float32)[:map_size[0], :map_size[1]]
    final_vector_matrix = sc.ndimage.zoom(small_vector_matrix * scale_down, zoom=[zoom[0], zoom[1], 1], order=0, output=np.float32)[:map_size[0], :map_size[1]]

    for i, (x, y) in enumerate(coordinates_array):
        x_final = int((map_size[0] + x) % map_size[0])
        y_final = int((map_size[1] + y) % map_size[1])
        final_matrix[x_final, y_final] = i+1
        noise_array[x_final, y_final] = np.zeros(2, dtype=np.float32)  # Reset the noise array for the final matrix

    final_matrix, _, __ = _jump_flood_algorithm(final_matrix,
                                                noise_matrix=noise_array,
                                                step_size=2 ** (1 + int(np.log(max(map_size)))),
                                                distance_matrix=final_distance_matrix,
                                                vector_matrix=final_vector_matrix)

    return final_matrix


def find_subnodal_pixel_ownership(coordinates_array: np.array,
                                  map_size: np.array,
                                  noise_array: np.array = np.array,
                                  scale_down: int = 4):
    # Runs a jump flood algorithm on a scaled down version of the map, then scales up and redoes the algorithm more
    # finely. This speeds up runtime significantly. The main function of the JFA is run in Numba, which speeds up the
    # code and allows it to be run in parallel on CPU or GPU.

    small_x_size = int(map_size[0] / scale_down)
    small_y_size = int(map_size[1] / scale_down)
    subnode_matrix = np.zeros((small_x_size, small_y_size), dtype=np.uint16)
    small_matrix = np.zeros((small_x_size, small_y_size), dtype=np.uint16)

    s_distance_matrix = np.full((small_x_size, small_y_size), np.inf, dtype=np.float32)
    s_vector_matrix = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)
    small_noise_array = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)

    for i, (x, y) in enumerate(coordinates_array):
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        subnode_matrix[x_small, y_small] = i+1
        s_distance_matrix[x_small, y_small] = 0

    subnode_matrix, _, _ = _jump_flood_algorithm(subnode_matrix,
                                                 noise_matrix=small_noise_array,
                                                 step_size=2 ** (int(1 + np.log(max(map_size) / scale_down))),
                                                 distance_matrix=s_distance_matrix,
                                                 vector_matrix=s_vector_matrix)

    s_distance_matrix = np.full((small_x_size, small_y_size), np.inf, dtype=np.float32)
    s_vector_matrix = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)

    # Create subnodes and assign them to the relevent provinces
    engine = sc.stats.qmc.PoissonDisk(d=2, radius=0.025)
    sample = engine.fill_space()
    subnode_array = np.zeros(len(coordinates_array) + len(sample) + 1, dtype=np.uint16)

    for j, subnode in enumerate(sample):
        x, y = int(subnode[0] * small_x_size), int(subnode[1] * small_y_size)
        subnode_array[j + len(coordinates_array) + 1] = subnode_matrix[x, y]
        small_matrix[x, y] = j + len(coordinates_array) + 1
        s_distance_matrix[x, y] = 0

    for j, (x, y) in enumerate(coordinates_array):
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        small_matrix[x_small, y_small] = j + 1
        s_distance_matrix[x_small, y_small] = 0

        subnode_array[j + 1] = j + 1

    small_matrix, small_distance_matrix, small_vector_matrix = _jump_flood_algorithm(small_matrix,
                                                                                     noise_matrix=small_noise_array,
                                                                                     step_size=2 ** (1 + int(np.log(max(map_size) / scale_down))),
                                                                                     distance_matrix=s_distance_matrix,
                                                                                     vector_matrix=s_vector_matrix)

    # Scale the matrix back up and run a JFA again to refine
    zoom = np.divide(map_size, small_matrix.shape)
    final_matrix = sc.ndimage.zoom(small_matrix, zoom=zoom, order=0, output=np.uint16)[:map_size[0], :map_size[1]]
    final_distance_matrix = sc.ndimage.zoom(small_distance_matrix * scale_down, zoom=zoom, order=0, output=np.float32)[:map_size[0], :map_size[1]]
    final_vector_matrix = sc.ndimage.zoom(small_vector_matrix * scale_down, zoom=[zoom[0], zoom[1], 1], order=0, output=np.float32)[:map_size[0], :map_size[1]]

    for i, (x, y) in enumerate(coordinates_array):
        x_final = int((map_size[0] + x) % map_size[0])
        y_final = int((map_size[1] + y) % map_size[1])
        final_matrix[x_final, y_final] = i+1
        noise_array[x_final, y_final] = np.zeros(2, dtype=np.float32)  # Reset the noise array for the final matrix

    final_matrix, _, __ = _jump_flood_algorithm(final_matrix,
                                                noise_matrix=noise_array,
                                                step_size=2 ** (1 + int(np.log(max(map_size)))),
                                                distance_matrix=final_distance_matrix,
                                                vector_matrix=final_vector_matrix)

    final_matrix = numba_subnode_cleanup(final_matrix, subnode_array)

    return final_matrix


def pb_pixel_allocation(pixel_matrix):
    pixel_ownership_list = list()
    x_size, y_size = pixel_matrix.shape
    for y in range(y_size):
        pb_length = 1
        first_prov_index = 0
        first_x = 0
        first_y = y
        for x in range(x_size):
            current_prov_index = pixel_matrix[x, y]
            if current_prov_index == first_prov_index:  # If this is the same prov just extend the length and continue
                pb_length += 1
            elif first_prov_index == 0:  # If we're still on the first pb, assign it properly and carry on
                first_prov_index = current_prov_index
            else:  # If it's a new province id, append the last pb string and start a new one
                pixel_ownership_list.append([first_x, first_y, pb_length, first_prov_index])
                first_prov_index = current_prov_index
                first_x = x
                first_y = y
                pb_length = 1
        pixel_ownership_list.append([first_x, first_y, pb_length, first_prov_index])  # final section

    return pixel_ownership_list


def pb_2_map(pb_list, width, height):
    pixel_map = np.array((width, height), dtype=np.int16)

    for pb in pb_list:
        x, y, len, owner = pb
        for pixel in range(len):
            pixel_map[x + pixel][y] = owner
            coordinate_dict[owner].append([x + pixel, y])

            province = self.province_list[owner - 1]

    # self.height_map[x + pixel][y] = 20
    # if province.terrain_int & 4:
    #     self.height_map[x + pixel][y] = -30
    # if province.terrain_int & 2052 == 2052:
    #     self.height_map[x + pixel][y] = -100
    return pixel_map


@njit(parallel=True, cache=True)
def fast_matrix_2_pb(pixel_matrix):
    x_size, y_size = pixel_matrix.shape
    flat = pixel_matrix.T.flatten()
    change_indices = np.nonzero(np.append(flat, 0) != np.append(0, flat))[0]
    rle_array = (np.append(change_indices, change_indices[-1]) - np.append(0, change_indices))[0:-1]
    remaining = y_size * x_size - np.sum(rle_array)

    if remaining > 0:
        rle_array = np.append(rle_array, remaining)

    return list(rle_array)


# @njit(parallel=True, cache=True)
def fast_pb_2_matrix(pb_list, width, height):
    pixel_map = np.zeros((width, height), dtype=np.uint16)
    for x, y, l, i in pb_list:
        pixel_map[x:x+l+1, y] = i

    return pixel_map


def pixel_matrix_2_bitmap_arrays(pixel_matrix):
    bitmaps = list()

    for i in np.unique(pixel_matrix):  # Goes through all unique province indices and finds the bitmaps
        bitmap_array = pixel_matrix == i
        non_zero = np.nonzero(bitmap_array)  # Reduce the size by finding the bounding box and recording the positional coordinates
        x_1 = non_zero[0].min()
        x_2 = non_zero[0].max()
        y_1 = non_zero[1].min()
        y_2 = non_zero[1].max()

        bitmaps.append([i, (x_1, y_1), np.multiply(254, bitmap_array[x_1:x_2 + 1, y_1:y_2 + 1]).astype(dtype=np.uint8)])

    return bitmaps


def pixel_matrix_2_borders_array(pixel_matrix, thickness=1):
    left_matrix = np.roll(pixel_matrix, shift=-2 * thickness, axis=0)
    down_matrix = np.roll(pixel_matrix, shift=-2 * thickness, axis=1)
    border_array = (down_matrix != pixel_matrix) | (left_matrix != pixel_matrix)

    return np.multiply(254, np.roll(border_array, shift=thickness, axis=(0, 1))).astype(dtype=np.uint8)


@njit(parallel=True, cache=True)
def numba_height_map(pixel_map, height_array):
    height_map = np.zeros(pixel_map.shape, dtype=np.int16)

    for x in prange(pixel_map.shape[0]):
        for y in prange(pixel_map.shape[1]):
            height_map[x, y] = height_array[pixel_map[x, y]]

    return height_map


@njit(parallel=True, cache=True)
def numba_subnode_cleanup(pixel_map, subnode_array):

    output_map = np.zeros(pixel_map.shape, dtype=np.uint16)

    for x in prange(pixel_map.shape[0]):
        for y in prange(pixel_map.shape[1]):
            output_map[x, y] = subnode_array[pixel_map[x, y]]

    return output_map
