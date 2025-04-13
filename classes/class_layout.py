import matplotlib.pyplot as plt

from . import *


class DominionsLayout:

    def __init__(self, map_class):  # This class handles layout

        self.map = map_class
        self.seed = map_class.seed
        self.map_size = map_class.map_size
        self.wraparound = self.map.wraparound

        # Region level layout - supersedes planes
        self.region_planes = None
        self.region_types = None
        self.region_graph = None

        # Province level layout - list per plane
        self.province_graphs = [None for _ in range(10)]
        self.edge_types = [list() for _ in range(10)]
        self.neighbours = [list() for _ in range(10)]
        self.special_neighbours = [list() for _ in range(10)]
        self.gates = [list() for _ in range(10)]
        self.min_dist = [np.inf for _ in range(10)]

    def generate_region_layout(self,
                               settings: DreamAtlasSettings,
                               map_size: np.array,
                               nation_list: list,
                               seed: int = None):
        dibber(self, seed)  # Setting random seed

        teams = dict()
        ug_starts = 0
        for nation in nation_list:  # Analyse player teams
            iid, team = nation.iid, nation.team
            if team not in teams:
                teams[team] = [iid]
            else:
                teams[team].append(iid)
            if nation.home_plane == 2:
                ug_starts += 1

        homeland_region_num = len(nation_list)
        periphery_region_num = int(0.5 * settings.player_neighbours * homeland_region_num)
        blockers = 5 * (settings.cave_region_num + ug_starts) + 50
        num_regions = homeland_region_num + periphery_region_num + settings.throne_region_num + settings.water_region_num + settings.cave_region_num + settings.vast_region_num + blockers

        self.region_graph = DreamAtlasGraph(size=num_regions, map_size=map_size, wraparound=self.wraparound)
        initial_graph = copy(rd.choice(DATASET_GRAPHS[len(nation_list)][settings.player_neighbours]))  # Select an initial layout

        self.region_planes = dict()
        self.region_types = dict()
        r = 0

        # Add Homeland regions
        for i, nation in enumerate(nation_list):
            for j in initial_graph[i+1]:
                self.region_graph.connect_nodes(i, j-1)
            self.region_graph.planes[i] = nation.home_plane
            self.region_planes[r] = nation.home_plane
            self.region_types[r] = 0
            r += 1

        weights = dict()
        for i in range(len(nation_list)):
            weights[i] = 1

        self.region_graph.embed_graph(initial_graph, seed)
        self.region_graph.spring_adjustment()

        # homeland_coords = self.region_graph.coordinates[0:len(nation_list)]
        # codebook, distortion = sccvq.kmeans(obs=np.array(homeland_coords, dtype=np.float32), k_or_guess=len(teams))
        # code, distortion = sccvq.vq(homeland_coords, codebook)
        # print(code)
        # for j in code:

        # Add Peripheral regions
        done_edges = set()
        for i, j in self.region_graph.get_all_connections():
            if (j, i) not in done_edges:
                done_edges.add((i, j))
                self.region_graph.insert_connection(i, j, r)
                self.region_planes[r] = 1
                self.region_types[r] = 1
                r += 1

        faces, centroids = self.region_graph.get_faces_centroids()

        region_types = [(settings.throne_region_num, 2, 'throne'),
                        (settings.water_region_num, 3, 'water'),
                        (settings.cave_region_num, 4, 'cave'),
                        (settings.vast_region_num, 5, 'vast')]

        extras = False
        for region_num, region_type, region_name in region_types:
            if region_num == 0:
                continue
            if region_num <= len(centroids):
                codebook, distortion = sccvq.kmeans(obs=np.array(centroids, dtype=np.float32), k_or_guess=region_num)
            else:
                codebook = centroids
                extras = True

            for coordinate in codebook:
                closest_distance = np.inf
                for j, centroid in enumerate(centroids):
                    distance = np.linalg.norm(np.subtract(centroid, coordinate))
                    if distance < closest_distance:
                        best_centroid = centroid
                        closest_distance = distance
                        face = faces[j]
                centroids.remove(best_centroid)
                faces.remove(face)

                self.region_graph.insert_face(face, r, best_centroid)
                self.region_planes[r] = 1 if region_name != 'cave' else 2
                self.region_graph.planes[r] = self.region_planes[r]
                self.region_types[r] = region_type
                r += 1

            if extras:
                extras = False
                faces, centroids = self.region_graph.get_faces_centroids()
                codebook, distortion = sccvq.kmeans(obs=np.array(centroids, dtype=np.float32), k_or_guess=region_num-len(codebook))

                for coordinate in codebook:
                    closest_distance = np.inf
                    for j, centroid in enumerate(centroids):
                        distance = np.linalg.norm(np.subtract(centroid, coordinate))
                        if distance < closest_distance:
                            best_centroid = centroid
                            closest_distance = distance
                            face = faces[j]
                    centroids.remove(best_centroid)
                    faces.remove(face)

                    self.region_graph.insert_face(face, r, best_centroid)
                    self.region_planes[r] = 1 if region_name != 'cave' else 2
                    self.region_graph.planes[r] = self.region_planes[r]
                    self.region_types[r] = region_type
                    r += 1

        # Add Blocker regions - mountain blocker regions go into non-triangular surface faces then cave walls between cave regions
        # faces, centroids = self.region_graph.get_faces_centroids(planes=[1])
        faces = set()
        for i, face in enumerate(faces):
            if len(face) > 3:
                self.region_graph.insert_face(face, r, centroids[i])
                self.region_planes[r] = 1
                self.region_graph.planes[r] = self.region_planes[r]
                self.region_types[r] = 6
                r += 1

        self.region_graph.make_delaunay_graph(planes=[2])  # Adding cave walls
        faces, centroids = self.region_graph.get_faces_centroids(planes=[2])
        for i, j in self.region_graph.get_all_connections():
            if self.region_planes[i] == 2 and self.region_planes[j] == 2:
                self.region_graph.insert_connection(i, j, r)
                self.region_planes[r] = 2
                self.region_graph.planes[r] = self.region_planes[r]
                self.region_types[r] = 8
                r += 1

        for i, face in enumerate(faces):
            self.region_graph.insert_face(face, r, centroids[i])
            self.region_planes[r] = 2
            self.region_graph.planes[r] = self.region_planes[r]
            self.region_types[r] = 8
            r += 1

        # Final Adjustment
        self.region_graph.spring_adjustment()

    def generate_province_layout(self,
                                 province_list,
                                 plane: int,
                                 seed: int = None):
        dibber(self, seed)  # Setting random seed

        self.province_graphs[plane] = DreamAtlasGraph(len(province_list), map_size=self.map_size[plane], wraparound=self.wraparound)
        for i, province in enumerate(province_list):
            self.province_graphs[plane].coordinates[i] = province.coordinates
            # self.province_graphs[plane].weights[i] = province.size

        self.province_graphs[plane].make_delaunay_graph()
        self.province_graphs[plane].spring_adjustment()

    def generate_neighbours(self, plane: int):

        self.neighbours[plane] = list()
        done_edges = set()
        for i, j in self.province_graphs[plane].get_all_connections():
            if (j, i) not in done_edges:
                done_edges.add((i, j))
                self.neighbours[plane].append([i+1, j+1])
        self.min_dist[plane] = self.province_graphs[plane].get_min_dist()

    def generate_special_neighbours(self,
                                    plane: int,
                                    seed: int = None):
        dibber(self, seed)  # Setting random seed

        if not self.neighbours[plane]:
            raise Exception('No neighbours')
        self.special_neighbours[plane] = list()
        index_2_prov = dict()
        for province in self.map.province_list[plane]:
            index_2_prov[province.index] = province

        for i, j in self.neighbours[plane]:  # Randomly assigns special connections
            i_j_provs = [index_2_prov[i], index_2_prov[j]]
            choice = int(rd.choices(SPECIAL_NEIGHBOUR, NEIGHBOUR_SPECIAL_WEIGHTS)[0][0])
            fail = False
            for index in range(2):
                ti = i_j_provs[index].terrain_int
                if i_j_provs[index].capital_location:  # Ignore caps
                    fail = True
                elif has_terrain(ti, 68719476736):  # if cave wall
                    self.special_neighbours[plane].append([i, j, 4])
                    fail = True
                elif self.region_types[i_j_provs[index].parent_region.index] == 6:  # if blocker
                    self.special_neighbours[plane].append([i, j, 36])
                    fail = True
                elif has_terrain(ti, 4):
                    fail = True
                elif has_terrain(ti, 4096):
                    fail = True
                elif (choice == 33 or choice == 36) and not has_terrain(ti, 8388608):
                    i_j_provs[index].terrain_int += 8388608
            if not fail and choice != 0:
                self.special_neighbours[plane].append([i, j, choice])

    def generate_gates(self, region_list, seed: int = None):
        dibber(self, seed)  # Setting random seed
        self.gates = [[] for _ in range(10)]
        gate = 1

        for region_type in [0, 4]:
            for i, i_region in enumerate(region_list[region_type]):

                if self.region_planes[i_region.index] == 2:
                    possible_j_regions = list()
                    for j, j_region in enumerate(region_list[1]):
                        if self.region_graph.graph[i_region.index, j_region.index]:
                            possible_j_regions.append(j_region)
                    rd.shuffle(possible_j_regions)

                    gates_num = REGION_CAVE_INFO[self.map.settings.cave_region_type][4]  # How many gates per region
                    start = 0
                    if region_type == 0:
                        gates_num = 3
                        start = 1

                    i_provinces = rd.sample(i_region.provinces[start:], k=gates_num)
                    for j, j_region in enumerate(possible_j_regions[0:gates_num]):
                        for province in j_region.provinces:
                            if not province.has_gate:
                                j_province = province
                        j_province.has_gate = True
                        self.gates[1].append([j_province.index, gate])
                        self.gates[2].append([i_provinces[j].index, gate])
                        gate += 1

    def plot(self):

        fix_reg, ax_reg = plt.subplots()

        # Plot regions
        virtual_graph, virtual_coordinates = self.region_graph.get_virtual_graph()

        for i, (x, y) in enumerate(virtual_coordinates):  # region connections
            if i in self.region_types:
                for j in np.argwhere(virtual_graph[i, :] == 1):
                    j = j[0]
                    x2, y2 = virtual_coordinates[j]
                    ax_reg.plot([x, x2], [y, y2], 'k-')

        region_colours = ['g*', 'rD', 'y^', 'bo', 'rv', 'ms', 'kX', 'kX', 'kX']
        for i, (x, y) in enumerate(virtual_coordinates):  # region connections
            if i in self.region_types:
                ax_reg.plot(x, y, region_colours[self.region_types[i]])
                ax_reg.text(x, y, str(i))

        ax_reg.set(xlim=(0, self.map_size[1][0]), ylim=(0, self.map_size[1][1]))

        # # Plot provinces
        # for i, plane in enumerate(self.map.planes):
        #     ax = ax_provinces[i]
        #     virtual_graph, virtual_coordinates = make_virtual_graph(self.graph[plane], self.coordinates[plane], self.darts[plane], self.map.map_size[plane])
        #     for j in virtual_graph:  # region connections
        #         x0, y0 = virtual_coordinates[j]
        #         for k in virtual_graph[j]:
        #             x1, y1 = virtual_coordinates[k]
        #             ax.plot([x0, x1], [y0, y1], 'k-')
        #
        #     for j in self.graph[plane]:
        #         x0, y0 = self.coordinates[plane][j]
        #         ax.plot(x0, y0, 'ro')
        #         ax.text(x0, y0, str(j))
        #     ax.set(xlim=(0, self.map_size[plane][0]), ylim=(0, self.map_size[plane][1]))

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
