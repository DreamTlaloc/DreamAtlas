from DreamAtlas import *
from DreamAtlas.functions.numba_pixel_mapping import _numba_height_map


def generator_dreamatlas(settings: type(DreamAtlasSettings),
                         ui=None,
                         seed: int = None):
    def estimate_time(settings):
        return 45
    if ui is not None:
        ui.progress_bar.start(estimate_time(settings) * 10)

    def generator_logging(text):
        if ui is not None:
            ui.status_label_var.set(text)
        else:
            print(f'{text}')

    map_class = DominionsMap()
    map_class.map_title = settings.map_title
    map_class.settings, map_class.seed = settings, settings.seed
    dibber(map_class, seed)

    # Loading nations and making the nation -> graph dict
    generator_logging('Making nations...')
    nation_list = list()
    for nation_data in settings.vanilla_nations:
        nation_list.append(Nation(nation_data))
    for custom_nation_data in settings.custom_nations:
        nation_list.append(CustomNation(custom_nation_data))
    for generic_nation_data in settings.generic_nations:
        nation_list.append(GenericNation(generic_nation_data))
    # rd.shuffle(nation_list)
    for i, nation in enumerate(nation_list):
        nation.iid = i

    # Generate the player layout graph, determine the map size/region scale
    generator_logging('Making region layout...')
    pixels = np.asarray([0, 3000000], dtype=np.uint32)
    homeland_region_num = len(nation_list)
    periphery_region_num = int(0.5 * settings.player_neighbours * homeland_region_num)

    pixels[0] += PIXELS_PER_PROVINCE * homeland_region_num * settings.homeland_size
    pixels[0] += PIXELS_PER_PROVINCE * periphery_region_num * settings.periphery_size
    pixels[0] += PIXELS_PER_PROVINCE * settings.throne_region_num
    pixels[0] += PIXELS_PER_PROVINCE * settings.water_region_num * REGION_WATER_INFO[settings.water_region_type][2]
    pixels[0] += PIXELS_PER_PROVINCE * settings.vast_region_num
    pixels[1] += PIXELS_PER_PROVINCE * settings.cave_region_num * REGION_CAVE_INFO[settings.cave_region_type][2] * 4

    map_class.map_size[1:3] = np.outer(np.sqrt(pixels), np.asarray([1, 0.588])).round(decimals=-2).astype(dtype=np.uint32)
    map_class.wraparound = NEIGHBOURS[settings.wraparound]
    map_class.scale[1] = min(map_class.map_size[1]) * np.asarray([0.035])
    map_class.scale[2] = min(map_class.map_size[2]) * np.asarray([0.03])
    map_class.planes = [1, 2]
    layout = DominionsLayout(map_class)
    layout.generate_region_layout(settings=map_class.settings, map_size=map_class.map_size[1], nation_list=nation_list, seed=map_class.seed)

    # Assemble the regions and generate the initial province layout
    generator_logging('Making regions....')

    province_index = [1 for _ in range(10)]
    province_list = [[] for _ in range(10)]
    region_list = [[] for _ in range(9)]
    terrain_list = [[] for _ in range(10)]

    for i in layout.region_types:  # Generate all the regions
        region_type = layout.region_types[i]

        if region_type == 0:  # Generate the homelands
            new_region = HomelandRegion(index=i, nation=nation_list[i], settings=settings, seed=map_class.seed)
        elif region_type == 1:  # Generate the peripherals
            nations = list()
            for j in layout.region_graph.get_node_connections(i):
                if j < len(nation_list):
                    nations.append(nation_list[int(j)])
            new_region = PeripheryRegion(index=i, nations=nations, settings=settings, seed=map_class.seed)
        elif region_type == 2:  # Generate the thrones
            new_region = ThroneRegion(index=i, settings=map_class.settings, seed=map_class.seed)
        elif region_type == 3:  # Generate the water regions
            new_region = WaterRegion(index=i, settings=map_class.settings, seed=map_class.seed)
        elif region_type == 4:  # Generate the cave regions
            new_region = CaveRegion(index=i, settings=map_class.settings, seed=map_class.seed)
        elif region_type == 5:  # Generate the vast regions
            new_region = VastRegion(index=i, settings=map_class.settings, seed=map_class.seed)
        else:  # Generate the blocker regions
            new_region = BlockerRegion(index=i, blocker=region_type, settings=map_class.settings, seed=map_class.seed)

        region_list[region_type].append(new_region)
        new_region.generate_graph()
        new_region.generate_terrain()
        new_region.generate_population()
        new_region.embed_region(global_coordinates=layout.region_graph.coordinates[i], scale=map_class.scale, map_size=map_class.map_size)

        for province in new_region.provinces:
            province.index = province_index[new_region.plane]
            province_list[new_region.plane].append(province)
            province_index[new_region.plane] += 1

    special_start_locations = list()    # Generate the special start locations
    for region in region_list[0]:
        if type(region.nation) is not GenericNation:
            for province in region.provinces:
                if province.capital_location:
                    special_start_index = province.index
                    if region.plane == 2:   # Curse you Illwinterrr!!!!!!
                        special_start_index += len(province_list[1])
            special_start_locations.append([region.nation.index, int(special_start_index)])

    map_class.region_list = region_list
    map_class.province_list = province_list

    generator_logging('Map assembly....')

    for plane in map_class.planes:
        layout.generate_province_layout(province_list[plane], plane=plane)
        layout.generate_neighbours(plane=plane)
        layout.generate_special_neighbours(plane=plane)
    layout.generate_gates(region_list=region_list)

    # Check to add omni here
    if settings.omniscience:
        for province in province_list[2]:
            fail = False
            if not has_terrain(province.terrain_int, 68719476736):
                continue
            else:
                for j in layout.province_graphs[2].get_node_connections(province.index-1):
                    i_province = province_list[2][j[0]]
                    if not has_terrain(i_province.terrain_int, 68719476736):
                        fail = True
            if not fail:
                break

        special_start_locations.append([499, len(province_list[1]) + province.index])
        province.has_commands = True
        province.terrain_int = 4 + 4096 + 67108864
        province.population = 10000
        province.size = 2
        province.shape = 3

    for plane in map_class.planes:
        for province in province_list[plane]:  # Do this here in case of terrain changes from mountains (curse you Illwinter!!!!)
            terrain_list[plane].append([province.index, province.terrain_int])
            province.coordinates = layout.province_graphs[plane].coordinates[province.index-1]

    map_class.special_start_locations = special_start_locations
    map_class.terrain_list = terrain_list
    map_class.neighbour_list = layout.neighbours
    map_class.min_dist = layout.min_dist
    map_class.special_neighbour_list = layout.special_neighbours
    map_class.gate_list = layout.gates
    map_class.layout = layout

    ########################################################################################################################
    # Do pixel mapping
    generator_logging('Pixel mapping...')
    for plane in map_class.planes:
        shapes = dict()
        for province in province_list[plane]:
            shapes[province.index] = [province.shape, 1 / province.shape]

        map_class.pixel_map[plane] = find_pixel_ownership(layout.province_graphs[plane].coordinates, map_class.map_size[plane], shapes, hwrap=True, vwrap=True, scale_down=8)
        map_class.pixel_owner_list[plane] = pb_pixel_allocation(map_class.pixel_map[plane])

        height_array = np.zeros(len(province_list[plane])+1, dtype=np.int16)
        for province in map_class.province_list[plane]:
            height = 20
            if has_terrain(province.terrain_int, 4):
                height = -30
            if has_terrain(province.terrain_int, 2052):
                height = -100
            if has_terrain(province.terrain_int, 68719476736):  # testing cave wall rendering hypothesis
                height = -100
            height_array[province.index] = height

        map_class.height_map[plane] = _numba_height_map(map_class.pixel_map[plane], height_array)

    map_class.ygg_desc = 'example desc'
    map_class.ygg_emoji = ':earth_africa:'

    generator_logging('Loading into UI...')
    if ui is not None:
        ui.progress_bar.stop()
    return map_class
