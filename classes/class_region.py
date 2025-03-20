from .class_province import Province
from .class_settings import DreamAtlasSettings
from . import *


class Region:

    def __init__(self,
                 index: int,
                 settings: DreamAtlasSettings,
                 seed: int = None):

        self.index = index
        self.settings = settings

        if seed is None:
            seed = self.settings.seed
        self.seed = seed * index            # Alters the random seed based on characteristics

        self.graph = dict()         # Graph is a dictionary for the province graph
        self.provinces = list()     # Provinces is a list of the province classes in the region

        self.name = 'testname'
        self.plane = 1
        self.terrain_pref = None
        self.layout = None

        self.region_size = 1
        self.anchor_connections = 1

    def generate_graph(self, seed: int = None):
        dibber(self, seed)
        self.provinces = list()

        spread_range = np.pi / self.anchor_connections
        base_rotation = np.random.uniform(0, np.pi)
        theta = np.linspace(0, 2*np.pi, self.anchor_connections, endpoint=False) + np.random.uniform(base_rotation, base_rotation + spread_range, self.anchor_connections)

        for i in range(self.region_size):
            province = Province(index=i, parent_region=self, plane=self.plane)

            if i == 0:  # Generating the anchor province
                province.coordinates = [0, 0]

            elif i <= self.anchor_connections:  # Generate the anchor connections, rotating randomly, then adding some small random angle/radius change
                province.coordinates = np.asarray([np.cos(theta[i-1]), np.sin(theta[i-1])])

            else:  # Place the remaining extra provinces attached to non-anchor provinces
                j = rd.choice(range(1, 1 + self.anchor_connections))
                j_coordinates = self.provinces[j].coordinates
                phi = theta[j-1] + np.random.uniform(0, 0.5*spread_range)
                province.coordinates = j_coordinates + np.random.uniform(0.85, 1.15) * np.asarray([np.cos(phi), np.sin(phi)])

            self.provinces.append(province)

    def generate_terrain(self, seed: int = None):  # This is the basic generate terrain, specific region types differ
        dibber(self, seed)

        terrain_picks = rd.choices(TERRAIN_PREF_BITS, weights=self.terrain_pref, k=self.region_size)  # Pick a selection of primary terrains for this region

        for i in range(self.region_size):  # Apply the terrain and land/sea/cave tags to each province

            province = self.provinces[i]
            terrain_set = {0, 512, 134217728}  # Plains, No Start, Bad Throne Location

            if province.plane == 2:
                terrain_set.add(4096)  # Cave layer
                terrain_set.add(576460752303423488)

            if i == 0:  # Anchor province
                if self.layout[0] == 0:
                    terrain_set.add(4)

            elif i <= self.anchor_connections:  # Circle provinces
                terrain_set.add(terrain_picks[i])
                if i > self.layout[1] * self.anchor_connections:  # Circle sea/land split
                    terrain_set.add(4)  # Sea

            else:  # Extra provinces
                terrain_set.add(terrain_picks[i])
                if rd.random() > self.layout[2]:  # land/sea
                    terrain_set.add(4)  # Sea
                    if 32 in terrain_set or 64 in terrain_set or 256 in terrain_set:
                        terrain_set.remove(terrain_picks[i])

            province.terrain_int = sum(terrain_set)

    def generate_population(self, seed: int = None):  # Generates the population for the region

        if self.settings.pop_balancing == 0:  # No population balancing
            return
        elif self.settings.pop_balancing == 2:  # Re-seed with same seed for all regions in this case
            seed = self.settings.seed
        dibber(self, seed)

        populations = np.linspace(0,  self.region_size, self.region_size+1, dtype=np.float32)
        populations[1:self.region_size] += np.random.uniform(-0.4, 0.4, self.region_size-1)
        populations = np.sort(np.diff(populations * AGE_POPULATION_SIZES[self.settings.age]))

        self.provinces.sort(key=lambda p: terrain_2_population_weight(p.terrain_int))

        for i, province in enumerate(self.provinces):
            province.has_commands = True
            province.population = int(populations[i])
            if province.capital_location:  # Assign capital population
                province.population = CAPITAL_POPULATION

    def embed_region(self,
                     global_coordinates: list,
                     scale: list[list[int, int], ...],
                     map_size: list[list[int, int], ...],
                     seed: int = None):  # Embeds the region in a global space
        dibber(self, seed)

        for province in self.provinces:
            province.coordinates = np.mod(np.add(global_coordinates, np.multiply(scale[self.plane],province.coordinates)), map_size[self.plane], dtype=np.float32, casting='unsafe')
            province.size, province.shape = find_shape_size(province, self.settings)

    def plot(self):

        # Making the figures (graph, terrain, population)
        fig, axs = plt.subplots(1, 3)
        ax_graph, ax_terrain, ax_population = axs
        plot_size = (500, 500)
        z_graph = np.zeros(plot_size)
        z_terrain = np.zeros(plot_size)
        z_population = np.zeros(plot_size)

        # Make the contourf z objects to be plotted
        points = list()
        for province in self.provinces:
            index = province.index
            x, y = province.coordinates
            points.append([index, x, y])

        pixel_map = find_pixel_ownership(points, plot_size, hwrap=False, vwrap=False, scale_down=8, minkowski_dist=3)
        for x in range(plot_size[0]):
            for y in range(plot_size[1]):
                this_index = pixel_map[x][y]
                z_graph[y][x] = this_index
                terrain_list = terrain_int2list(self.provinces[this_index - 1].terrain_int)
                for terrain in terrain_list:
                    z_terrain[y][x] += TERRAIN_2_HEIGHTS_DICT[terrain]
                z_population[y][x] = self.provinces[this_index - 1].population

        # Plotting the contourf and the province border contour map
        levels = len(self.graph)
        ax_graph.imshow(z_graph, cmap=cm.Set1)
        ax_graph.contour(z_graph, levels=levels, colors=['white', ])
        ax_graph.set_title('Provinces')
        ax_terrain.imshow(z_terrain, vmin=-200, vmax=600, cmap=cm.terrain)
        ax_terrain.contour(z_graph, levels=levels, colors=['white', ])
        ax_terrain.set_title('Terrain')
        ax_population.imshow(z_population, vmin=0, vmax=45000, cmap=cm.YlGn)
        ax_population.contour(z_graph, levels=levels, colors=['white', ])
        ax_population.set_title('Population')
        fig.suptitle('%s Region' % self.name)

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string


class HomelandRegion(Region):

    def __init__(self, index: int, nation: Nation, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.nation = nation
        self.terrain_pref = nation.terrain_profile
        self.layout = nation.layout
        self.terrain = nation.terrain
        self.plane = nation.home_plane
        self.region_size = self.settings.homeland_size
        self.anchor_connections = self.settings.cap_connections
        self.name = nation.name

    def generate_graph(self, seed: int = None):
        dibber(self, seed)
        self.provinces = list()

        spread_range = np.pi / self.anchor_connections
        theta = np.linspace(0, 2*np.pi, self.anchor_connections, endpoint=False)

        for i in range(self.region_size):
            province = Province(index=i, parent_region=self, plane=self.plane)

            if i == 0:  # Generating the anchor province
                province.coordinates = [0, 0]
                province.capital_location = True
                if type(self.nation) is not GenericNation:
                    province.special_capital = self.nation.index

            elif i <= self.anchor_connections:  # Generate the anchor connections, rotating randomly, then adding some small random angle/radius change
                province.coordinates = np.asarray([np.cos(theta[i-1]), np.sin(theta[i-1])])

            else:  # Place the remaining extra provinces attached to non-anchor provinces
                j = rd.choice(range(1, 1 + self.anchor_connections))
                j_coordinates = self.provinces[j].coordinates
                phi = theta[j-1] + np.random.uniform(0, 0.5*spread_range)
                province.coordinates = j_coordinates + np.random.uniform(0.85, 1.15) * np.asarray([np.cos(phi), np.sin(phi)])

            self.provinces.append(province)

    def generate_terrain(self, seed: int = None):  # This is the basic generate terrain, specific region types differ
        dibber(self, seed)

        terrain_picks = rd.choices(TERRAIN_PREF_BITS, weights=self.terrain_pref, k=self.region_size)  # Pick a selection of primary terrains for this region

        for i in range(self.region_size):  # Apply the terrain and land/sea/cave tags to each province

            province = self.provinces[i]
            terrain_set = {0, 512, 134217728}  # Plains, No Start, Bad Throne Location

            if province.plane == 2:
                terrain_set.add(4096)  # Cave layer

            if i == 0:  # Anchor province
                terrain_set.remove(512)  # Remove no start
                terrain_set.add(67108864)  # Good start location
                terrain_set.add(self.terrain)  # Capital terrain

            elif i <= self.anchor_connections:  # Circle provinces
                terrain_set.add(terrain_picks[i])
                if i > self.layout[1] * self.anchor_connections:  # Circle sea/land split
                    terrain_set.add(4)  # Sea

            else:  # Extra provinces
                terrain_set.add(terrain_picks[i])
                if rd.random() > self.layout[2]:  # land/sea
                    terrain_set.add(4)  # Sea
                    if 32 in terrain_set or 64 in terrain_set or 256 in terrain_set:
                        terrain_set.remove(terrain_picks[i])

            province.terrain_int = sum(terrain_set)


class PeripheryRegion(Region):

    def __init__(self, index: int, nations: list, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.nations = nations
        self.region_size = self.settings.periphery_size
        self.anchor_connections = self.settings.periphery_size - 1
        self.terrain_pref, self.layout = nations_2_periphery(nations)
        self.name = f'{nations[0].name}-{nations[1].name} border'


class ThroneRegion(Region):

    def __init__(self, index: int, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.terrain_pref, self.layout = TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND
        self.name = f'Throne {index}'

    def generate_terrain(self, seed: int = None):  # This is the basic generate terrain, specific region types differ
        dibber(self, seed)

        for i in range(self.region_size):  # Apply the terrain and land/sea/cave tags to each province

            province = self.provinces[i]
            terrain_set = {0, 512, 33554432}  # Plains, No Start, Good Throne Location
            province.terrain_int = sum(terrain_set)


class WaterRegion(Region):

    def __init__(self, index: int, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.terrain_pref, self.layout, self.region_size, self.anchor_connections = REGION_WATER_INFO[settings.water_region_type]
        self.name = f'Sea {index}'


class CaveRegion(Region):

    def __init__(self, index: int, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.terrain = 4096
        self.plane = 2
        self.terrain_pref, self.layout, self.region_size, self.anchor_connections = REGION_CAVE_INFO[settings.cave_region_type]
        self.name = f'Cave {index}'


class VastRegion(Region):

    def __init__(self, index: int, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.terrain = rd.choice(REGION_VAST_INFO)
        self.name = f'Vast {index}'

    def generate_terrain(self, seed: int = None):  # This is the basic generate terrain, specific region types differ
        dibber(self, seed)

        for i in range(self.region_size):  # Apply the terrain and land/sea/cave tags to each province
            province = self.provinces[i]
            province.terrain_int = self.terrain + 8589934592

    def generate_population(self, seed: int = None):

        if self.settings.pop_balancing == 0:  # No population balancing
            return

        for i, province in enumerate(self.provinces):
            province.has_commands = True
            province.population = 8000


class BlockerRegion(Region):

    def __init__(self, index: int, blocker: int, settings: DreamAtlasSettings, seed: int = None):
        super().__init__(index, settings, seed)

        self.blocker = blocker
        self.plane, self.terrain, self.region_size, self.anchor_connections = REGION_BLOCKER_INFO[blocker]

    def generate_terrain(self, seed: int = None):  # This is the basic generate terrain, specific region types differ
        dibber(self, seed)

        for i in range(self.region_size):  # Apply the terrain and land/sea/cave tags to each province
            province = self.provinces[i]
            province.terrain_int = self.terrain

    def generate_population(self, seed: int = None):

        if self.settings.pop_balancing == 0:  # No population balancing
            return

        for i, province in enumerate(self.provinces):
            province.has_commands = True
            province.population = 0

