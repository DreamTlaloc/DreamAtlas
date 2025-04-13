# Imports all the DreamAtlas functionality and dependencies
from DreamAtlas import *


@njit(fastmath=True, cache=True)
def minkowski(v, p, ip):
    return (abs(v[0]) ** p + abs(v[1]) ** p) ** ip


@njit(parallel=True, cache=True, fastmath=True)
def _jump_flood_algorithm(pixel_matrix: np.array,
                          step_size: int,
                          shape_array: np.array,
                          distance_matrix: np.array,
                          vector_matrix: np.array,
                          hwrap: bool = True,
                          vwrap: bool = True):

    shape_x, shape_y = np.shape(pixel_matrix)

    end = False
    ping_matrix = pixel_matrix
    pong_matrix = pixel_matrix
    ping_distance_matrix = distance_matrix
    pong_distance_matrix = distance_matrix
    ping_vector_matrix = vector_matrix
    pong_vector_matrix = vector_matrix
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
                        q_vector = np.subtract(ping_vector_matrix[rx, ry], n)
                        # q_dist = np.linalg.norm(q_vector, ord=shape_array[q-1])
                        q_dist = minkowski(q_vector, shape_array[q-1, 0], shape_array[q-1, 1])
                        if p == 0:  # if our pixel is empty, populate it with q
                            pong_distance_matrix[x, y] = q_dist
                            pong_vector_matrix[x, y] = q_vector
                            pong_matrix[x, y] = q
                        elif ping_distance_matrix[x, y] > q_dist:  # if our pixel is not empty, see if q is closer than p and if so populate it with q
                            pong_distance_matrix[x, y] = q_dist
                            pong_vector_matrix[x, y] = q_vector
                            pong_matrix[x, y] = q

        ping_matrix = pong_matrix
        ping_distance_matrix = pong_distance_matrix
        ping_vector_matrix = pong_vector_matrix

        if end and step_size == 1:  # Breaking the while loop
            break
        if step_size == 1:  # Does a final pass
            step_size = 16
            end = True

    return ping_matrix, ping_distance_matrix, ping_vector_matrix


def find_pixel_ownership(coordinates_array: np.array,
                         map_size: np.array,
                         shapes: dict,
                         hwrap: bool = True,
                         vwrap: bool = True,
                         scale_down: int = 8):
    # Runs a jump flood algorithm on a scaled down version of the map, then scales up and redoes the algorithm more
    # finely. This speeds up runtime significantly. The main function of the JFA is run in Numba, which speeds up the
    # code and allows it to be run in parallel on CPU or GPU.

    small_x_size = int(map_size[0] / scale_down)
    small_y_size = int(map_size[1] / scale_down)
    small_matrix = np.zeros((small_x_size, small_y_size), dtype=np.uint16)
    dict_size = len(coordinates_array)

    shape_array = np.full((dict_size, 2), 2, dtype=np.float32)
    s_distance_matrix = np.full((small_x_size, small_y_size), np.inf, dtype=np.float32)
    s_vector_matrix = np.zeros((small_x_size, small_y_size, 2), dtype=np.float32)

    for i, (x, y) in enumerate(coordinates_array):
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        small_matrix[x_small, y_small] = i+1
        s_distance_matrix[x_small, y_small] = 0
        shape_array[i] = shapes[i+1]

    small_output_matrix, small_distance_matrix, small_vector_matrix = _jump_flood_algorithm(small_matrix,
                                                                                            step_size=2 ** (int(1 + np.log(max(map_size) / scale_down))),
                                                                                            shape_array=shape_array,
                                                                                            distance_matrix=s_distance_matrix,
                                                                                            vector_matrix=s_vector_matrix,
                                                                                            hwrap=hwrap,
                                                                                            vwrap=vwrap)

    # Scale the matrix back up and run a JFA again to refine
    zoom = np.divide(map_size, small_output_matrix.shape)
    final_matrix = sc.ndimage.zoom(small_output_matrix, zoom=zoom, order=0, output=np.uint16)[:map_size[0], :map_size[1]]
    final_distance_matrix = sc.ndimage.zoom(small_distance_matrix * scale_down, zoom=zoom, order=0, output=np.float32)[:map_size[0], :map_size[1]]
    final_vector_matrix = sc.ndimage.zoom(small_vector_matrix * scale_down, zoom=[zoom[0], zoom[1], 1], order=0, output=np.float32)[:map_size[0], :map_size[1]]

    for i, (x, y) in enumerate(coordinates_array):
        x_final = int((map_size[0] + x) % map_size[0])
        y_final = int((map_size[1] + y) % map_size[1])
        final_matrix[x_final, y_final] = i+1

    final_matrix, _, __ = _jump_flood_algorithm(final_matrix,
                                                step_size=2 ** (int(np.log(max(map_size)))),
                                                shape_array=shape_array,
                                                distance_matrix=final_distance_matrix,
                                                vector_matrix=final_vector_matrix,
                                                hwrap=hwrap,
                                                vwrap=vwrap)

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
def _numba_height_map(pixel_map, height_array):
    height_map = np.zeros(pixel_map.shape, dtype=np.int16)

    for x in prange(pixel_map.shape[0]):
        for y in prange(pixel_map.shape[1]):
            height_map[x, y] = height_array[pixel_map[x, y]]

    return height_map