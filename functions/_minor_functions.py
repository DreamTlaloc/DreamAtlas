from DreamAtlas import *


def terrain_int2list(terrain_int):          # Function for separating terrain int into the components
    terrain_list = list()
    binary = bin(terrain_int)[:1:-1]
    for x in range(len(binary)):
        if int(binary[x]):
            terrain_list.append(2**x)
    return terrain_list


def find_shape_size(province, settings):  # Function for calculating the size of a province

    terrain_int = province.terrain_int
    terrain_list = terrain_int2list(terrain_int)
    size = 1
    shape = 2

    # size
    if settings.pop_balancing != 0:
        size *= 0.5 + 0.0125 * np.sqrt(province.population)  # size - population
    if has_terrain(province.terrain_int, 67108864):
        size *= 1.5
    if has_terrain(province.terrain_int, 4096):
        size *= 1.5

    # shape
    for terrain in TERRAIN_2_SHAPES_DICT:
        if terrain in terrain_list:
            shape *= TERRAIN_2_SHAPES_DICT[terrain]

    return size, shape


def has_terrain(ti, t):  # Checks terrain ints for specific terrains

    return ti & t == t


def terrain_2_resource_stats(terrain_int_list: list[int],
                             age: int):
    average = 91
    average *= AGE_POPULATION_MODIFIERS[age]
    for terrain_int in terrain_int_list:
        if terrain_int & 1:
            average *= 0.5
        elif terrain_int & 2:
            average *= 1.5
        if terrain_int & 256:
            average *= 0.5

        for specific_terrain in RESOURCE_SPECIFIC_TERRAINS:
            if has_terrain(terrain_int, specific_terrain):
                average *= RESOURCE_SPECIFIC_TERRAINS[specific_terrain]

    return average


def terrain_2_population_weight(terrain_int: int) -> int:

    weight = 4
    for bit in TERRAIN_PREF_BITS[1:]:
        if has_terrain(terrain_int, bit):
            weight = TERRAIN_POPULATION_ORDER[bit]

    return weight


def nations_2_periphery(nations):
    t1 = TERRAIN_PREFERENCES.index(nations[0].terrain_profile)
    l1 = LAYOUT_PREFERENCES.index(nations[0].layout)
    t2 = TERRAIN_PREFERENCES.index(nations[1].terrain_profile)
    l2 = LAYOUT_PREFERENCES.index(nations[1].layout)
    return PERIPHERY_INFO[PERIPHERY_DATA[7*l1+t1][7*l2+t2]-1]


COLOURS_PROVINCES = mpl.colormaps['tab20'].resampled(1000)
COLOURS_REGIONS = mpl.colormaps['Pastel2'].resampled(300)
COLOURS_TERRAIN = mpl.colormaps['terrain']
COLOURS_POPULATION = mpl.colormaps['Greens']
COLOURS_RESOURCES = mpl.colormaps['Oranges']


def provinces_2_colours(province_list):  # Creates the pre-defined colours for a whole province list

    colours = list()
    for province in province_list:
        colours.append(single_province_2_colours(province))

    return colours


def single_province_2_colours(province):  # ['Art', 'Provinces', 'Regions', 'Terrain', 'Population', 'Resources']

    colour = ['pink'] * 6

    colour[1] = mpl.colors.rgb2hex(COLOURS_PROVINCES(province.index))
    if province.parent_region is None:
        colour[2] = mpl.colors.rgb2hex(COLOURS_REGIONS(1))
    else:
        colour[2] = mpl.colors.rgb2hex(COLOURS_REGIONS(province.parent_region.index))
    colour[3] = mpl.colors.rgb2hex(COLOURS_TERRAIN(province.terrain_int))
    try:
        colour[4] = mpl.colors.rgb2hex(COLOURS_POPULATION(np.sqrt(province.population/50000)))
    except:
        colour[4] = mpl.colors.rgb2hex(COLOURS_POPULATION(np.sqrt(0.2)))
    colour[5] = mpl.colors.rgb2hex(COLOURS_RESOURCES(0.003 * terrain_2_resource_stats(terrain_int2list(province.terrain_int), age=1)))

    return colour


def find_graph_faces(graph, coordinates, darts, map_size):

    edges_set, embedding = set(), dict()
    for i in graph:  # edges_set is an undirected graph as a set of undirected edges
        j_angles = list()
        for j in graph[i]:
            edges_set |= {(i, j), (j, i)}
            vector = coordinates[j] + np.multiply(darts[i][graph[i].index(j)], map_size) - coordinates[i]
            angle = 90-np.angle(vector[0] + vector[1] * 1j, deg=True)
            j_angles.append([j, angle])

        j_angles.sort(key=lambda x: x[1])
        embedding[i] = [x[0] for x in j_angles]  # Format: v1:[v2,v3], v2:[v1], v3:[v1] clockwise ordering of neighbors at each vertex

    faces, path = list(), list()  # Storage for face paths
    path.append((i, j))
    edges_set -= {(i, j)}

    while len(edges_set) > 0:  # Trace faces
        neighbors = embedding[path[-1][-1]]
        next_node = neighbors[(neighbors.index(path[-1][-2]) + 1) % (len(neighbors))]
        tup = (path[-1][-1], next_node)
        if tup == path[0]:
            faces.append(path)
            path = list()
            for edge in edges_set:  # Starts next path
                path.append(edge)
                edges_set -= {edge}
                break  # Only one iteration
        else:
            path.append(tup)
            edges_set -= {tup}
    if len(path) != 0:
        faces.append(path)

    centroids = list()
    for face in faces:
        shift = np.subtract(np.divide(map_size, 2), coordinates[face[0][0]])
        total = np.zeros(2)
        for edge in face:
            i = edge[0]
            total += (np.add(coordinates[i], shift)) % map_size
        coordinate = (-shift + total / len(face)) % map_size
        centroids.append((int(coordinate[0]), int(coordinate[1])))

    return faces, centroids


def dibber(class_object, seed):  # Setting the random seed, when no seed is provided the class seed is used
    if seed is None:
        seed = class_object.seed
    rd.seed(seed)
    np.random.seed(seed)
