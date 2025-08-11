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


def terrain_2_height(terrain_int: int) -> int:

    height = 0

    for terrain in terrain_int2list(terrain_int):
        if terrain in TERRAIN_2_HEIGHTS_DICT:
            height += TERRAIN_2_HEIGHTS_DICT[terrain]

    return height


def nations_2_periphery(nations):
    t1 = TERRAIN_PREFERENCES.index(nations[0].terrain_profile)
    l1 = LAYOUT_PREFERENCES.index(nations[0].layout)
    t2 = TERRAIN_PREFERENCES.index(nations[1].terrain_profile)
    l2 = LAYOUT_PREFERENCES.index(nations[1].layout)
    return PERIPHERY_INFO[PERIPHERY_DATA[7*l1+t1][7*l2+t2]-1]


def terrain_2_colour(terrain_int: int) -> float:

    col_float = 0.95
    for terrain in COLOURS_DICT:  # Check for terrain types
        if has_terrain(terrain_int, terrain):
            col_float = COLOURS_DICT[terrain]

    return col_float


def provinces_2_colours(province_list):  # Creates the pre-defined colours for a whole province list

    colours = list()
    for province in province_list:
        colours.append(single_province_2_colours(province, total_provs=len(province_list)))

    return colours


def single_province_2_colours(province, total_provs):  # ['Art', 'Provinces', 'Regions', 'Terrain', 'Population', 'Resources']

    colour = ['pink'] * 6

    colour[1] = mpl.colors.rgb2hex(COLOURS_PROVINCES(0.1 + (province.index % 20)/30))
    if province.parent_region is None:
        colour[2] = mpl.colors.rgb2hex(COLOURS_REGIONS(1))
    else:
        colour[2] = mpl.colors.rgb2hex(COLOURS_REGIONS((province.parent_region.index % 20)/20))
    colour[3] = mpl.colors.rgb2hex(COLOURS_TERRAIN(terrain_2_colour(province.terrain_int)))
    try:
        colour[4] = mpl.colors.rgb2hex(COLOURS_POPULATION(np.sqrt(province.population/50000)))
    except:
        colour[4] = mpl.colors.rgb2hex(COLOURS_POPULATION(np.sqrt(0.2)))
    colour[5] = mpl.colors.rgb2hex(COLOURS_RESOURCES(0.003 * terrain_2_resource_stats(terrain_int2list(province.terrain_int), age=1)))

    return colour


def dibber(class_object, seed):  # Setting the random seed, when no seed is provided the class seed is used
    if seed is None:
        seed = class_object.seed
    rd.seed(seed)
    np.random.seed(seed)
