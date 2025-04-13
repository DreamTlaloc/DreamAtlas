# Imports all the DreamAtlas functionality and dependencies
import matplotlib.pyplot as plt

from . import *


class DominionsMap:

    """
    A class to represent a map in the Dominions game.

    Attributes
    ----------
    settings : None
        Placeholder for settings.
    homeland_list : list
        List of homelands.
    periphery_list : list
        List of peripheries.
    throne_list : list
        List of thrones.
    province_list : list
        List of provinces for each plane.
    armies_list : list
        List of armies for each plane.
    pretenders_list : list
        List of pretenders for each plane.
    map_title : str
        Title of the map.
    image_file : list
        List of image files for each plane.
    image_pil : list
        List of PIL images for each plane.
    map_size : list
        List of map sizes for each plane.
    scale : list
        List of scales for each plane.
    planes : set
        Set of planes.
    dom_version : str
        Version of Dominions.
    scenario : bool
        Indicates if the map is a scenario.
    description : str
        Description of the map.
    neighbour_list : list
        List of neighbours for each plane.
    special_neighbour_list : list
        List of special neighbours for each plane.
    pixel_owner_list : list
        List of pixel owners for each plane.
    province_names_list : list
        List of province names for each plane.
    terrain_list : list
        List of terrains for each plane.
    population_list : list
        List of populations for each plane.
    gate_list : list
        List of gates for each plane.
    map_text_colour : list
        List of map text colours.
    map_dom_colour : list
        List of map dominion colours.
    max_sail_distance : list
        List of maximum sail distances for each plane.
    magic_sites : list
        List of magic sites for each plane.
    capital_names : bool
        Indicates if capital names are used.
    allowed_nations_list : list
        List of allowed nations.
    computer_player_list : list
        List of computer players.
    ai_allies_list : list
        List of AI allies.
    victory_type : list
        List of victory types.
    cannot_win_list : list
        List of provinces that cannot win.
    victory_point_provinces : list
        List of victory point provinces for each plane.
    start_locations : list
        List of start locations for each plane.
    no_start_locations : list
        List of no start locations for each plane.
    special_start_locations : list
        List of special start locations for each plane.
    team_start_locations : list
        List of team start locations for each plane.
    seed : int
        Seed for random generation.
    layout : None
        Placeholder for layout.
    pixel_map : list
        List of pixel maps for each plane.
    height_map : list
        List of height maps for each plane.
    min_dist : list
        List of minimum distances for each plane.
    province_capital_locations : list
        List of province capital locations for each plane.

    Methods
    -------
    __init__():
        Initializes the map with default values.
    load_file(filepath, plane=1):
        Loads a map file.
    fill_dreamatlas(plane_image_types):
        Fills the map with DreamAtlas data.
    load_folder(folderpath):
        Loads all map files from a folder.
    make_map_file(plane, filepath):
        Creates a .map file.
    make_d6m(plane, filepath):
        Creates a .d6m file.
    publish(location=None, name=None, art_style=0):
        Publishes the map.
    plot():
        Plots the map.
    __str__():
        Returns a string representation of the map.
    """

    def __init__(self):  # Map classes always initialise empty to be filled in later

        # DreamAtlas required data
        self.settings = None
        self.region_list = [[] for _ in range(7)]
        self.province_list = [[] for _ in range(10)]
        self.armies_list = [[] for _ in range(10)]
        self.pretenders_list = [[] for _ in range(10)]

        # Required map data/commands
        self.map_title = 'DreamAtlas_map'
        self.image_file = [None for _ in range(10)]
        self.image_pil = [None for _ in range(10)]
        self.map_size = [[0, 0] for _ in range(10)]
        self.scale = [[0, 0] for _ in range(10)]
        self.planes = set()

        # Basic map data/commands
        self.dom_version = '600'
        self.scenario = False
        self.description = "An exciting map made using Tlaloc\'s DreamAtlas!"
        self.neighbour_list = [[] for _ in range(10)]
        self.special_neighbour_list = [[] for _ in range(10)]
        self.pixel_owner_list = [[] for _ in range(10)]
        self.province_names_list = [[] for _ in range(10)]
        self.terrain_list = [[] for _ in range(10)]
        self.population_list = [[] for _ in range(10)]
        self.gate_list = [[] for _ in range(10)]

        # Advanced map data/commands
        self.map_text_colour = [1.0, 1.0, 1.0, 0]
        self.map_dom_colour = [255, 202, 255, 5]
        self.max_sail_distance = [2 for _ in range(10)]
        self.magic_sites = [60 for _ in range(10)]
        self.capital_names = True
        self.allowed_nations_list = list()
        self.computer_player_list = list()
        self.ai_allies_list = list()
        self.victory_type = [6, 12]
        self.cannot_win_list = list()
        self.victory_point_provinces = [[] for _ in range(10)]

        # Start location data/commands
        self.start_locations = [[] for _ in range(10)]
        self.no_start_locations = [[] for _ in range(10)]
        self.special_start_locations = [[] for _ in range(10)]
        self.team_start_locations = [[] for _ in range(10)]

        # Meta data (for later)
        self.seed = 0
        self.layout = None
        self.pixel_map = [None for _ in range(10)]
        self.pixel_owner_list = [[] for _ in range(10)]
        self.height_map = [None for _ in range(10)]
        self.min_dist = [None for _ in range(10)]
        self.province_capital_locations = [[] for _ in range(10)]
        self.wraparound = NEIGHBOURS_FULL

        self.ygg_desc = 'DreamAtlas empty map'
        self.ygg_emoji = ':smile:'

    def load_file(self, filepath, plane=1):  # Instructs the map class to load in a file.

        if filepath.endswith('.map'):
            with open(filepath, 'r') as f:
                current_province = 1
                lines = f.readlines()
                for line in lines:
                    if line[0] != '#':
                        continue
                    line = line.split()

                    if line[0] == '#setland':
                        current_province = int(line[1])

                    if line[0] == '#dom2title':
                        self.map_title = line[1]
                    elif line[0] == '#imagefile':
                        self.image_file[plane] = line[1]
                    elif line[0] == '#mapsize':
                        self.map_size[plane] = [int(line[1]), int(line[2])]
                    elif line[0] == '#wraparound':
                        self.wraparound = NEIGHBOURS[3]
                    elif line[0] == '#domversion':
                        self.dom_version = int(line[1])
                    # if line[0] == '#winterimagefile':
                    #     self.winter_image_file = line[1]
                    elif line[0] == '#scenario':
                        self.scenario = True
                    elif line[0] == '#description':
                        self.description = ' '.join(line[1:])
                    elif line[0] == '#neighbour':
                        self.neighbour_list[plane].append([int(line[1]), int(line[2])])
                    elif line[0] == '#neighbourspec':
                        self.special_neighbour_list[plane].append([int(line[1]), int(line[2]), int(line[3])])
                    elif line[0] == '#gate':
                        self.gate_list[plane].append([int(line[1]), int(line[2])])
                    elif line[0] == '#pb':
                        self.pixel_owner_list[plane].append([int(line[1]), int(line[2]), int(line[3]), int(line[4])])
                    elif line[0] == '#landname':
                        self.province_names_list[plane].append([int(line[1]), ' '.join(line[2:])])

                    elif line[0] == '#terrain':
                        self.terrain_list[plane].append([int(line[1]), int(line[2])])

                    # setlands go here
                    elif line[0] == '#population':
                        self.population_list[plane].append([current_province, int(line[1])])

                    elif line[0] == '#maptextcol':
                        self.map_text_colour[plane] = [float(line[1]), float(line[2]), float(line[3]), float(line[4])]
                    elif line[0] == '#mapdomcol':
                        self.map_dom_colour[plane] = [int(line[1]), int(line[2]), int(line[3]), int(line[4])]
                    elif line[0] == '#saildist':
                        self.max_sail_distance[plane] = int(line[1])
                    elif line[0] == '#features':
                        self.magic_sites[plane] = int(line[1])
                    elif line[0] == '#nohomelandnames':
                        self.capital_names[plane] = True
                    # if line[0] == '#nonamefilter':
                    #     self.no_names = True
                    elif line[0] == '#allowedplayer':
                        self.allowed_nations_list.append(int(line[1]))
                    elif line[0] == '#computerplayer':
                        self.computer_player_list.append([int(line[1]), int(line[2])])
                    elif line[0] == '#allies':
                        self.ai_allies_list.append([int(line[1]), int(line[2])])
                    elif line[0] == '#victorycondition':
                        self.victory_type = [int(line[1]), int(line[2])]
                    elif line[0] == '#cannotwin':
                        self.cannot_win_list.append(int(line[1]))
                    elif line[0] == '#victorypoints ':
                        self.victory_point_provinces[plane].append([int(line[1]), int(line[2])])

                    elif line[0] == '#start':
                        self.start_locations[plane].append(int(line[1]))
                    elif line[0] == '#nostart':
                        self.no_start_locations[plane].append(int(line[1]))
                    elif line[0] == '#specstart':
                        self.special_start_locations[plane].append([int(line[1]), int(line[2])])
                    elif line[0] == '#teamstart':
                        self.special_start_locations[plane].append([int(line[1]), int(line[2])])

        elif filepath.endswith('.d6m'):  # THIS IS SLOW AS HELL RE-DO IN NUMPY
            with open(filepath, 'rb') as f:  # Read in the (little-endian) binary data

                magic_number1, file_version, width, height, spec, min_dist_dec, min_dist_real, nbr_provinces = struct.Struct("<iiiiqhii").unpack_from(f.read(struct.calcsize("<iiiiqhii")))
                self.map_size[plane][0] = width
                self.map_size[plane][1] = height
                self.min_dist[plane] = min_dist_real + min_dist_dec * 0.0001

                if magic_number1 == 898933:  # Is the correct magic number here?

                    self.province_capital_locations[plane] = np.zeros((nbr_provinces, 3), dtype=np.uint16)
                    height_array = np.zeros(width*height, dtype=np.int16)
                    pixel_array = np.zeros(width*height, dtype=np.uint16)

                    hhq_len = struct.calcsize("<hhq")
                    for i in range(nbr_provinces):
                        self.province_capital_locations[plane][i] = np.array(struct.Struct("<hhq").unpack_from(f.read(hhq_len)))

                    a_len = width * height
                    h_len = struct.calcsize("<h")
                    for i in range(a_len):
                        z = struct.Struct("<h").unpack_from(f.read(h_len))
                        height_array[i] = z[0]

                    for i in range(a_len):
                        z = struct.Struct("<h").unpack_from(f.read(h_len))
                        pixel_array[i] = z[0]

                    self.height_map[plane] = np.reshape(height_array, (width, height), order='F')
                    self.pixel_map[plane] = np.reshape(pixel_array, (width, height), order='F')

                    magic_number2 = struct.Struct("<i").unpack_from(f.read(struct.calcsize("<i")))
                    if magic_number2[0] != 1155:  # An incorrect magic number suggests .d6m file is incorrectly formatted
                        raise Exception('Error loading .d6m: Magic number 2 should be 1155 - got %i' % magic_number2[0])
                else:
                    raise Exception('Error loading .d6m: Magic number 1 should be 898933 - got %i' % magic_number1)

        elif filepath.endswith('.tga'):
            self.image_file[plane] = filepath
            self.image_pil[plane] = Image.open(filepath)
        else:
            raise Exception('DominionsMap can only load files of type .map, .d6m, .tga')

    def fill_dreamatlas(self, plane_image_types):

        self.layout = DominionsLayout(self)
        for plane in self.planes:
            self.layout.province_graphs[plane] = DreamAtlasGraph(size=len(self.terrain_list[plane]), map_size=self.map_size[plane], wraparound=self.wraparound)
            self.province_list[plane] = list()

            height_dict = dict()
            for i, terrain_int in self.terrain_list[plane]:
                new_province = Province(index=i, terrain_int=terrain_int, parent_region=None)
                self.province_list[plane].append(new_province)

                height_dict[i] = 0
                if has_terrain(terrain_int, 4) or has_terrain(terrain_int, 68719476736):
                    height_dict[i] = -100
                for j, population in self.population_list[plane]:
                    if i == j:
                        self.province_list[plane][-1].population = population

            for (i, j) in self.neighbour_list[plane]:
                self.layout.neighbours[plane].append([i-1, j-1])
                self.layout.province_graphs[plane].connect_nodes(i-1, j-1)

            for (i, j, c) in self.special_neighbour_list[plane]:
                self.layout.special_neighbours[plane].append([i, j, c])

            if self.pixel_map[plane] is None:
                self.pixel_map[plane] = fast_pb_2_matrix(self.pixel_owner_list[plane], width=self.map_size[plane][0], height=self.map_size[plane][1])

            if plane_image_types[plane] == '.d6m':
                for i, (x, y, spec) in enumerate(self.province_capital_locations[plane]):
                    self.layout.province_graphs[plane].coordinates[i] = [x, y]
                    for province in self.province_list[plane]:
                        if province.index == i+1:
                            province.coordinates = [x, y]
                            province.height = self.height_map[plane][x, y]

            elif plane_image_types[plane] == '.tga':

                all_capital_locations = list()
                pixels = self.image_pil[plane].load()
                for x in range(self.map_size[plane][0]):
                    for y in range(self.map_size[plane][1]):
                        yr = self.map_size[plane][1]-y-1
                        if pixels[x, y] == (255, 255, 255):
                            all_capital_locations.append((x, yr))

                for x, y in all_capital_locations:
                    i = self.pixel_map[plane][x, y]
                    self.layout.province_graphs[plane].coordinates[i-1] = [x, y]
                    for province in self.province_list[plane]:
                        if province.index == i:
                            province.coordinates = [x, y]

                self.height_map[plane] = np.vectorize(lambda i: height_dict[i])(self.pixel_map[plane])
                self.min_dist[plane] = self.layout.province_graphs[plane].get_min_dist()

            for i, j in self.layout.province_graphs[plane].get_all_connections():
                min_dist = np.inf
                for n in self.wraparound:
                    dist = self.layout.province_graphs[plane].get_length(i, j)
                    if dist < min_dist:
                        best_dart = n
                        min_dist = dist
                self.layout.province_graphs[plane].darts[i-1] = best_dart

    def load_folder(self, folderpath: str):
        plane_image_types = [None for _ in range(10)]
        if os.path.isdir(folderpath):  # parse files in directory, try to load all the files in
            for dirpath, dirnames, filenames in os.walk(folderpath):
                for file in filenames:
                    if file[-4:] in ['.map', '.d6m', '.tga']:
                        plane = 1
                        for i in range(2, 9):
                            if file[0:-4].endswith('_plane%i' % i):
                                plane = i
                        self.planes.add(plane)
                        self.load_file(os.path.join(dirpath, file), plane=plane)

                        if file[-4:] in ['.d6m', '.tga']:
                            plane_image_types[plane] = file[-4:]

        self.fill_dreamatlas(plane_image_types=plane_image_types)

    def make_map_file(self, plane: int, filepath: str):  # Instructs the map class to print a .map file with a specific name (should really be the map name)

        with open(filepath, 'w') as f:

            f.write('--This map file was made using DreamAtlas\n\n')
            f.write('--General Map Information\n')
            f.write('#dom2title %s\n' % self.map_title)
            f.write('#imagefile %s\n' % self.image_file[plane])
            # f.write('#winterimagefile %s\n' % self.winter_image_file[plane])
            f.write('#mapsize %s %s\n' % (self.map_size[plane][0], self.map_size[plane][1]))
            f.write('#wraparound\n')
            if not self.capital_names:
                f.write('#nohomelandnames\n')
            if self.scenario:
                f.write('#scenario\n')
            if self.dom_version is not None:
                f.write('#domversion %s\n' % self.dom_version)
            f.write('#mapnohide\n')
            f.write('#maptextcol ' + ' '.join(map(str, self.map_text_colour)) + '\n')
            f.write('#mapdomcol ' + ' '.join(map(str, self.map_dom_colour)) + '\n')
            if plane == 2:
                f.write('#planename The Realm Beneath\n')
            # if self.victory_type is not None:
            #     f.write('#victorycondition %s %s\n' % (self.victory_type[0], self.victory_type[1]))

            f.write('#nodeepcaves\n')
            f.write('#nodeepchoice\n')
            if self.max_sail_distance[plane] is not None:
                f.write('#saildist %s\n' % self.max_sail_distance[plane])
            if self.magic_sites[plane] is not None:
                f.write('#features %s\n' % self.magic_sites[plane])
            f.write('#description %s\n' % self.description)

            # Nation info
            f.write('\n--Nation info\n')
            # if len(self.allowed_nations_list) != 0:
            #     for entry in range(len(self.allowed_nations_list)):
            #         f.write('#allowedplayer %s\n' % self.allowed_nations_list[entry])
            if len(self.computer_player_list) != 0:
                for entry in range(len(self.computer_player_list)):
                    f.write('#computerplayer ' + ' '.join(map(str, self.computer_player_list[entry])) + '\n')
            if len(self.ai_allies_list) != 0:
                for entry in range(len(self.ai_allies_list)):
                    f.write('#allies ' + ' '.join(map(str, self.ai_allies_list[entry])) + '\n')
            if len(self.cannot_win_list) != 0:
                for entry in range(len(self.cannot_win_list)):
                    f.write('#cannotwin %s\n' % self.cannot_win_list[entry])

            f.write('\n--Province start info\n')
            if len(self.start_locations[plane]) != 0:
                for entry in range(len(self.start_locations[plane])):
                    f.write('#start %s\n' % self.start_locations[plane][entry])
            if len(self.no_start_locations[plane]) != 0:
                for entry in range(len(self.no_start_locations[plane])):
                    f.write('#nostart %s\n' % self.no_start_locations[plane][entry])
            if plane == 1:
                if len(self.special_start_locations) != 0:
                    for entry in range(len(self.special_start_locations)):
                        f.write('#specstart ' + ' '.join(map(str, self.special_start_locations[entry])) + '\n')
            if len(self.team_start_locations[plane]) != 0:
                for entry in range(len(self.team_start_locations[plane])):
                    f.write('#teamstart ' + ' '.join(map(str, self.team_start_locations[plane][entry])) + '\n')

            # Unique province info
            if len(self.victory_point_provinces[plane]) != 0:
                for entry in range(len(self.victory_point_provinces[plane])):
                    f.write('#victorypoints ' + ' '.join(map(str, self.victory_point_provinces[plane][entry])) + '\n')

            if len(self.province_names_list[plane]) != 0:
                f.write('\n--Unique province names\n')
                for entry in range(len(self.province_names_list[plane])):
                    f.write('#landname ' + ' '.join(map(str, self.province_names_list[plane][entry])) + '\n')

            # Terrain info
            if len(self.terrain_list[plane]) != 0:
                f.write('\n--Terrain info\n')
                for entry in range(len(self.terrain_list[plane])):
                    f.write('#terrain ' + ' '.join(map(str, self.terrain_list[plane][entry])) + '\n')

            # Neighbour info
            if len(self.neighbour_list[plane]) != 0:
                f.write('\n--Neighbour info\n')
                for entry in range(len(self.neighbour_list[plane])):
                    f.write('#neighbour ' + ' '.join(map(str, self.neighbour_list[plane][entry])) + '\n')
            if len(self.special_neighbour_list[plane]) != 0:
                f.write('\n--Special Neighbour info\n')
                for entry in range(len(self.special_neighbour_list[plane])):
                    f.write('#neighbourspec ' + ' '.join(map(str, self.special_neighbour_list[plane][entry])) + '\n')
            if len(self.gate_list[plane]) != 0:
                f.write('\n--Gate info\n')
                for i in self.gate_list[plane]:
                    f.write('#gate ' + ' '.join(map(str, i)) + '\n')

            f.write('\n--Province info\n')

            # Province commands
            for province in self.province_list[plane]:
                if province.has_commands:
                    f.write('#setland %i\n' % province.index)
                    if province.population is not None:
                        f.write('#population %i\n' % province.population)

            # Pixel ownership info
            f.write('\n--Pixel ownership info\n')
            if len(self.pixel_owner_list[plane]) != 0:
                for i in self.pixel_owner_list[plane]:
                    f.write('#pb ' + ' '.join(map(str, i)) + '\n')

            f.write('$ygg_desc ' + ' '.join(map(str, self.ygg_desc)) + '\n')
            f.write('$ygg_emoji ' + ' '.join(map(str, self.ygg_desc)) + '\n')

            f.write('\n--Version 1.1.6\n')
            if self.settings is not None:
                for attribute in self.settings.__dict__:
                    f.write('$%s %s\n' % (attribute, self.settings.__dict__[attribute]))

            f.write('\n--The End\n')
            f.write('--(P.S. if you\'re reading this then I hope you have a nice day)')

    def make_d6m(self,
                 plane: int,
                 filepath: str):

        with open(filepath, "wb") as f:  # Format is little endian binary which requires data to be converted

            f.write(struct.pack("<iiiiqhii", 898933, 3, int(self.map_size[plane][0]), int(self.map_size[plane][1]), 0,  # Write headline map data
                                int((self.min_dist[plane] % 1.0) * 10000), int(self.min_dist[plane]), int(len(self.province_list[plane]))))

            for province in self.province_list[plane]:  # Write pixel positions of each 'capital' (fort) and the 'spec' (if its deep sea, unknown why this is)
                x, y = province.coordinates
                f.write(struct.pack("<hhq", int(x), int(y), province.terrain_int & 2052))

            for height in np.ndarray.flatten(self.height_map[plane], order='F'):  # Write height for each pixel
                f.write(struct.pack("<h", int(height)))

            for owner in np.ndarray.flatten(self.pixel_map[plane], order='F'):  # Write ownership for each pixel
                f.write(struct.pack("<h", int(owner)))
            
            f.write(struct.pack("<i", 1155))  # Write final 'magic number' (allows dom6.exe to recognise the file)

    def publish(self,
                location: str = None,
                name: str = None,
                art_style: int = 0):

        if location is None:
            location = f"{ROOT_DIR}/maps//"
        if name is None:
            name = self.map_title

        os.mkdir(location)

        for plane in self.planes:
            plane_str = '_plane%i' % plane
            if plane == 1:
                plane_str = ''
            if art_style == 0:  # d6m art
                self.image_file[plane] = f'{name}{plane_str}.d6m'  # Make surface
                self.make_map_file(plane=plane, filepath=location+f'/{name}{plane_str}.map')
                self.make_d6m(plane=plane, filepath=location+f'/{name}{plane_str}.d6m')
            else:
                return Exception("No valid artstyle")

    def plot(self):  # Making the figures (general map, regions, terrain, population)

        fig1, axs1 = plt.subplots(len(self.planes), 1)
        fig2, axs2 = plt.subplots(len(self.planes), 1)
        fig3, axs3 = plt.subplots(len(self.planes), 1)
        fig4, axs4 = plt.subplots(len(self.planes), 1)

        for i, plane in enumerate(self.planes):
            map_x, map_y = self.map_size[plane]
            if len(self.planes) == 1:
                plane_axs = [axs1, axs2, axs3, axs4]
            else:
                plane_axs = [axs1[i], axs2[i], axs3[i], axs4[i]]

            for ax in plane_axs:
                ax.set(xlim=[0, map_x], ylim=[0, map_y])

            index_dict, region_dict, terrain_dict, population_dict = {0: 0}, {0: -1}, {0: -1}, {0: -1}
            for province in self.province_list[plane]:
                index_dict[province.index] = province.index
                region_dict[province.index] = province.parent_region.index
                terrain_dict[province.index] = 0
                for terrain in terrain_int2list(province.terrain_int):
                    if terrain in TERRAIN_2_HEIGHTS_DICT:
                        terrain_dict[province.index] += TERRAIN_2_HEIGHTS_DICT[terrain]
                population_dict[province.index] = province.population

            plotting_pixel_map = np.transpose(self.pixel_map[plane])
            plane_general = np.vectorize(lambda i: index_dict[i])(plotting_pixel_map)
            plane_regions = np.vectorize(lambda i: region_dict[i])(plotting_pixel_map)
            plane_terrain = np.vectorize(lambda i: terrain_dict[i])(plotting_pixel_map)
            plane_population = np.vectorize(lambda i: population_dict[i])(plotting_pixel_map)

            # Plotting the contourf and the province border contour map
            plane_axs[0].imshow(plane_general, cmap=cm.Pastel1)
            plane_axs[0].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[1].imshow(plane_regions, vmin=1, vmax=len(self.layout.region_graph), cmap=cm.tab20)
            plane_axs[1].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[2].imshow(plane_terrain, vmin=-200, vmax=600, cmap=cm.terrain)
            plane_axs[2].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[3].imshow(plane_population, cmap=cm.YlGn)
            plane_axs[3].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])

            virtual_graph, virtual_coordinates = make_virtual_graph(self.layout.graph[plane], self.layout.coordinates[plane], self.layout.darts[plane], self.map_size[plane])
            for i in virtual_graph:
                x0, y0 = virtual_coordinates[i]
                for j in virtual_graph[i]:
                    x1, y1 = virtual_coordinates[j]
                    for ax in plane_axs:
                        ax.plot([x0, x1], [y0, y1], 'k-')

            for province in self.province_list[plane]:
                x0, y0 = province.coordinates
                colour = 'ro'
                if has_terrain(province.terrain_int, 67108864):
                    colour = 'bo'
                elif has_terrain(province.terrain_int, 33554432):
                    colour = 'yo'
                for ax in plane_axs:
                    ax.plot(x0, y0, colour)
                    ax.text(x0, y0, str(province.index))

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
