import numpy as np
import scipy as sc
import minorminer as mnm
import networkx as ntx
import random as rd
from numba import njit, prange
from DreamAtlas.databases import NEIGHBOURS_FULL


def less_first(a, b):
    return [a, b] if a < b else [b, a]


@njit(cache=True)
def _numba_norm(v):
    return np.sqrt(abs(v[0]) * abs(v[0]) + abs(v[1]) * abs(v[1]))


@njit(parallel=True, cache=True)
def _numba_attractor_adjustment(graph: np.array,
                                coordinates: np.array,
                                darts: np.array,
                                attractor_array: np.array,
                                damping_ratio: float,
                                map_size: np.array,
                                iterations: int):
    dict_size = len(coordinates)
    net_velocity = np.zeros((dict_size, 2), dtype=np.float64)
    for _ in range(iterations):
        attractor_force = np.zeros((dict_size, 2), dtype=np.float64)
        for i in prange(dict_size):
            for j in np.argwhere(graph[i, :] == 1):
                if attractor_array[i, j]:
                    j = j[0]
                    attractor_force[i] += coordinates[j] + darts[i, j] * map_size - coordinates[i]

        net_velocity = damping_ratio * (net_velocity + attractor_force)

        equilibrium = 1
        for c in range(dict_size):  # Check if particles are within tolerance
            if _numba_norm(net_velocity[c]) > 0.00001:
                equilibrium = 0
                break

        coordinates += net_velocity
        for a in range(dict_size):  # Update the position
            for axis in range(2):
                if not (0 <= coordinates[a, axis] < map_size[axis]):
                    dart_change = -np.sign(coordinates[a, axis])
                    coordinates[a, axis] = coordinates[a, axis] % map_size[axis] - 25 * dart_change

                    for b in range(dict_size):  # Iterating over all of this vertex's connections
                        if graph[a, b]:
                            new_value = darts[a, b, axis] + dart_change
                            if new_value < -1:
                                new_value = 1
                            if new_value > 1:
                                new_value = -1

                            darts[a, b, axis] = new_value  # Setting the dart for this vertex
                            darts[b, a, axis] = -new_value  # Setting the dart for other vertex
        if equilibrium:
            break

    return coordinates, darts


@njit(parallel=True, cache=True)
def _numba_spring_adjustment(graph: np.array,
                             coordinates: np.array,
                             darts: np.array,
                             weight_array: np.array,
                             map_size: np.array,
                             ratios: np.array,
                             connections: np.array,
                             iterations: int):

    dict_size = len(coordinates)
    damping_ratio, spring_coefficient, base_length = ratios
    lengths = np.zeros((dict_size, dict_size), dtype=np.float32)

    for i, j in connections:
        lengths[i, j] = base_length * (weight_array[i] + weight_array[j])

    net_velocity = np.zeros((dict_size, 2), dtype=np.float32)
    for _ in range(iterations):
        net_spring_force = np.zeros((dict_size, 2), dtype=np.float32)
        for i in prange(dict_size):
            for j in np.argwhere(graph[i, :] == 1):
                j = j[0]
                vector = coordinates[j] + darts[i, j] * map_size - coordinates[i]

                net_spring_force[i] += vector * (1 - lengths[i, j] / (0.000001 + _numba_norm(vector)))

        net_velocity = damping_ratio * (net_velocity + spring_coefficient * net_spring_force)

        equilibrium = 1
        for c in range(dict_size):  # Check if particles are within tolerance
            if _numba_norm(net_velocity[c]) > 0.00001:
                equilibrium = 0
                break

        coordinates += net_velocity
        for a in range(dict_size):  # Update the position
            for axis in range(2):
                if not (0 <= coordinates[a, axis] < map_size[axis]):

                    for b in range(dict_size):  # Iterating over all of this vertex's connections
                        if graph[a, b]:
                            new_value = darts[a, b, axis] - np.sign(coordinates[a, axis])
                            if new_value < -1:
                                new_value = 1
                            if new_value > 1:
                                new_value = -1

                            darts[a, b, axis] = new_value  # Setting the dart for this vertex
                            darts[b, a, axis] = -new_value  # Setting the dart for other vertex

                    coordinates[a, axis] = coordinates[a, axis] % map_size[axis]

        if equilibrium:
            break

    return coordinates, darts


class DreamAtlasGraph:

    def __init__(self, size, map_size, wraparound):

        self.size = size
        self.graph = np.zeros((size, size), dtype=np.bool_)
        self.coordinates = np.zeros((size, 2), dtype=np.int32)
        self.darts = np.zeros((size, size, 2), dtype=np.int8)
        self.weights = np.ones(size, dtype=np.float32)
        self.planes = np.ones(size, dtype=np.int8)
        self.map_size = map_size
        self.wraparound = wraparound

        self.index_2_iid = dict()  # Maps the index to the disciples
        for i in range(size):
            self.index_2_iid[i] = i

        self.types = np.zeros(size, dtype=np.int8)
        self.plot_colour = ['r*' for _ in range(size)]  # Exclusively for plotting purposes

    def get_node_connections(self, i):
        return np.argwhere(self.graph[i, :] == 1)

    def get_all_connections(self):
        return np.argwhere(self.graph == 1)

    def get_vector(self, i, j):
        return self.coordinates[j] + self.darts[i, j] * self.map_size - self.coordinates[i]

    def get_length(self, i, j):
        return np.linalg.norm(self.get_vector(i, j))

    def get_unit_vector(self, i, j):
        return self.get_vector(i, j) / self.get_length(i, j)

    def get_min_dist(self):
        min_dist = np.inf
        for i, j in self.get_all_connections():
            dist = self.get_length(i, j)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def get_closest_dart(self, i, j):  # Returns the shortest dart from i to j

        min_dist = np.inf
        for n in NEIGHBOURS_FULL:
            v_vector = self.coordinates[j] + n * self.map_size - self.coordinates[i]
            dist = np.linalg.norm(v_vector)
            if dist < min_dist:
                min_dist = dist
                vector = v_vector

        dart = np.zeros(2, dtype=np.int8)
        for axis in [0, 1]:
            if not (0 <= self.coordinates[i][axis] + vector[axis] < self.map_size[axis]):
                dart[axis] = np.sign(self.coordinates[i][axis] + vector[axis])

        return dart

    def get_dart_from_coordinate(self, r1, r2):

        return np.floor_divide(r2, self.map_size) - np.floor_divide(r1, self.map_size)

    def disconnect_nodes(self, i, j):

        self.graph[i, j] = 0
        self.graph[j, i] = 0
        self.darts[i, j] = np.zeros(2, dtype=np.int8)
        self.darts[i, j] = np.zeros(2, dtype=np.int8)

    def connect_nodes(self, i, j):  # Connects nodes i, j

        self.graph[i, j] = 1
        self.graph[j, i] = 1

    def insert_connection(self, i, j, k):  # Inserts a new node k between two existing nodes i, j

        self.connect_nodes(i, k)
        self.connect_nodes(k, j)

        vector = self.coordinates[j] + self.darts[i, j] * self.map_size - self.coordinates[i]
        self.coordinates[k] = np.mod(self.coordinates[i] + 0.5 * vector, self.map_size)   # Find the coordinate between i, j

        i_dart, j_dart = np.zeros(2, dtype=np.int8), np.zeros(2, dtype=np.int8)

        for axis in [0, 1]:
            if not (0 <= self.coordinates[i][axis] + 0.5 * vector[axis] < self.map_size[axis]):
                i_dart[axis] = np.sign(self.coordinates[i][axis] + 0.5 * vector[axis])
            if not (0 <= self.coordinates[j][axis] - 0.5 * vector[axis] < self.map_size[axis]):
                j_dart[axis] = np.sign(self.coordinates[j][axis] - 0.5 * vector[axis])

        self.darts[i, k] = i_dart
        self.darts[k, i] = -i_dart
        self.darts[j, k] = j_dart
        self.darts[k, j] = -j_dart
        self.disconnect_nodes(i, j)

    def insert_face(self, face, i, r):

        self.coordinates[i] = r

        for j, _ in face:
            self.connect_nodes(i, j)
            dart = self.get_closest_dart(i, j)
            self.darts[i, j] = dart
            self.darts[j, i] = -dart

    def get_faces_centroids(self, planes=[1, 2]):

        edges_set, embedding = set(), dict()
        for i in range(self.size):  # edges_set is an undirected graph as a set of undirected edges
            if self.planes[i] in planes:
                connections = self.get_node_connections(i)
                j_angles = list()
                if len(connections) > 0:
                    for j in connections:
                        j = j[0]
                        if self.planes[j] in planes:
                            edges_set |= {(i, j), (j, i)}
                            vector = self.get_vector(i, j)
                            j_angles.append([j, np.angle(vector[0] + vector[1] * 1j, deg=True)])
                    if len(j_angles) > 0:
                        j_angles.sort(key=lambda x: x[1])
                        embedding[i] = [x[0] for x in j_angles]  # Format: v1:[v2,v3], v2:[v1], v3:[v1] clockwise ordering of neighbors at each vertex

        faces, path = list(), list()  # Storage for face paths
        first_key = list(embedding.keys())[0]
        first_path = (first_key, embedding[first_key][0])
        path.append(first_path)
        edges_set -= {first_path}

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
            shift = np.divide(self.map_size, 2) - self.coordinates[face[0][0]]
            total = np.zeros(2)
            for i, j in face:
                total += (self.coordinates[i] + shift) % self.map_size
            coordinate = (-shift + total / len(face)) % self.map_size
            centroids.append((int(coordinate[0]), int(coordinate[1])))

        return faces, centroids

    def embed_graph(self, s_graph, seed: int):

        # Set the graph size to embed (smaller is faster)
        scale_down = 100
        size = np.array(self.map_size / scale_down, dtype=np.uint32)
        connections = [[1, 0], [0, 1], [0, -1], [-1, 0]]

        # Make the H graph
        h_dict = dict()
        for x in range(size[0]):
            for y in range(size[1]):
                h_dict[(int(x * scale_down), int(y * scale_down))] = list()
                for connection in connections:
                    x_coord = int(((x + connection[0]) % size[0]) * scale_down)
                    y_coord = int(((y + connection[1]) % size[1]) * scale_down)
                    h_dict[(int(x * scale_down), int(y * scale_down))].append((x_coord, y_coord))
        h_graph = ntx.Graph(incoming_graph_data=h_dict)  # H graph
        s_graph = ntx.Graph(incoming_graph_data=s_graph)  # S graph

        for i in range(10):
            initial_embedding, worked = mnm.find_embedding(s_graph, h_graph, return_overlap=True, random_seed=seed)
            if worked:
                break
            else:
                seed = rd.randint(0, 100000)
                print('\033[31mEmbedding failed: Trying with new seed (%i)\x1b[0m' % seed)
        if not worked:
            raise Exception('EmbeddingError: Failed 10 times')

        # Form the subgraph of the target graph
        subgraph_nodes, node_2_r, node_2_a, counter = list(), dict(), dict(), 0
        a_2_r = dict()
        for i in range(1, 1 + len(s_graph)):
            for node in initial_embedding[i]:
                node_2_r[node] = i  # Node to real index
                node_2_a[node] = counter  # Node to attractor index
                a_2_r[counter] = i-1  # Attractor index to real index
                counter += 1
                subgraph_nodes.append(node)
        subgraph = h_graph.subgraph(subgraph_nodes)

        # Build the graph for attractor adjustment from the subgraph
        attractor_graph = np.zeros((len(subgraph), len(subgraph)), dtype=np.bool_)
        attractor_coordinates = np.zeros((len(subgraph), 2), dtype=np.float64)
        attractor_darts = np.zeros((len(subgraph), len(subgraph), 2), dtype=np.int8)

        for i in range(1, 1 + len(s_graph)):
            for node in initial_embedding[i]:  # Loop over all the embedded nodes in the subgraph
                attractor_coordinates[node_2_a[node]] = [node[0], node[1]]

                for edge in ntx.edges(subgraph, node):  # Add the connected subgraph nodes and darts
                    j = node_2_r[edge[1]]
                    if j == i or j in s_graph[i]:
                        dart = np.zeros(2, dtype=np.int8)
                        for axis in range(2):
                            if abs(edge[0][axis] - edge[1][axis]) > scale_down:
                                dart[axis] = np.sign(edge[0][axis] - edge[1][axis])
                        attractor_graph[node_2_a[node], node_2_a[edge[1]]] = 1
                        attractor_darts[node_2_a[node], node_2_a[edge[1]]] = dart

        attractor_array = np.zeros((len(subgraph), len(subgraph)), dtype=np.bool_)
        for i, j in np.argwhere(attractor_graph == 1):  # Determine which nodes are the same node and should be merged
            if a_2_r[i] == a_2_r[j]:
                attractor_array[i, j] = 1

        attractor_coordinates, attractor_darts = _numba_attractor_adjustment(attractor_graph, attractor_coordinates,
                                                                             attractor_darts, attractor_array,
                                                                             damping_ratio=0.314, map_size=self.map_size,
                                                                             iterations=3000)

        for i in range(1, 1 + len(s_graph)):  # Merge the alike vertices of the graph
            coordinate_sum = 0
            coordinates_offset = np.divide(self.map_size, 2) - attractor_coordinates[node_2_a[initial_embedding[i][0]]]
            for node in initial_embedding[i]:  # Loop over all the nodes for this vertex
                coordinate_sum += np.mod(coordinates_offset + attractor_coordinates[node_2_a[node]], self.map_size)
            self.coordinates[i - 1] = np.mod(np.subtract(coordinate_sum / len(initial_embedding[i]), coordinates_offset), self.map_size)

        dart_dict, dist_dict = dict(), dict()
        for i, j in np.argwhere(attractor_graph == 1):
            dist_dict[(a_2_r[i], a_2_r[j])] = np.inf

        for i, j in np.argwhere(attractor_graph == 1):
            k = a_2_r[i]
            l = a_2_r[j]
            if k != l:
                distance = np.linalg.norm(self.coordinates[l] + attractor_darts[i, j] * self.map_size - self.coordinates[k])
                if distance < dist_dict[(k, l)]:
                    dist_dict[(k, l)] = distance
                    dart_dict[(k, l)] = attractor_darts[i, j]

        for i, j in self.get_all_connections():  # Set the darts for the graph
            self.darts[i, j] = dart_dict[(i, j)]

    def embed_disciples(self, teams, seed):

        teams_graph = ntx.Graph()
        target_graph = ntx.Graph(incoming_graph_data=self.graph)
        nations = set()
        for i in teams:  # Create the subgraph for the team and add it to the disciples graph
            team = teams[i]
            teams_graph.add_node(team[0])
            for j in team:
                nations.add(j)
            for j, k in list(zip(team, team[1:])):
                teams_graph.add_edge(j, k)

        for i in range(10):
            initial_embedding, worked = mnm.find_embedding(teams_graph, target_graph, return_overlap=True, random_seed=seed)
            if worked:
                break
            else:
                seed = rd.randint(0, 100000)
                print('\033[31mDisciples embedding failed: Trying with new seed (%i)\x1b[0m' % seed)
        if not worked:
            raise Exception('DiscipleEmbeddingError: Failed 10 times')

        for i in nations:  # Assign the players to the graphs to be tracked later
            for node in initial_embedding[i]:
                self.index_2_iid[node] = i

    def make_delaunay_graph(self, planes=[1, 2]):

        points, key_list, counter = list(), dict(), 0
        for i in range(self.size):  # Set up the virtual points on the toroidal plane
            if self.planes[i] in planes:
                for j, n in enumerate(self.wraparound):
                    coordinate = self.coordinates[i] + n * self.map_size
                    points.append([coordinate[0], coordinate[1]])
                    key_list[counter] = i
                    counter += 1

        tri = sc.spatial.Delaunay(np.array(points), qhull_options='QJ')

        list_of_edges = list()
        for triangle in tri.simplices:
            for e1, e2 in [[0, 1], [1, 2], [2, 0]]:  # for all edges of triangle
                list_of_edges.append(less_first(triangle[e1], triangle[e2]))  # always lesser index first

        for p1, p2 in np.unique(list_of_edges, axis=0):  # remove duplicates
            i, j = key_list[p1], key_list[p2]
            i_c = tri.points[p1]
            if (0 <= i_c[0] < self.map_size[0]) and (0 <= i_c[1] < self.map_size[1]):  # only do this for nodes in the map
                self.connect_nodes(i, j)
                j_c = tri.points[p2]

                dart = np.zeros(2, dtype=np.int8)
                for axis in range(2):
                    if j_c[axis] < 0:
                        dart[axis] = -1
                    elif j_c[axis] >= self.map_size[axis]:
                        dart[axis] = 1
                self.darts[i, j] = dart
                self.darts[j, i] = -dart

    def get_small_delaunay(self, planes=[1, 2]):

        edges, coordinates, darts = list(), list(), list()

        points, key_list, counter = list(), dict(), 0
        for i in range(self.size):  # Set up the virtual points on the toroidal plane
            if self.planes[i] in planes:
                for j, n in enumerate(self.wraparound):
                    coordinate = self.coordinates[i] + n * self.map_size
                    points.append([coordinate[0], coordinate[1]])
                    key_list[counter] = i
                    counter += 1

        tri = sc.spatial.Delaunay(np.array(points), qhull_options='QJ')

        list_of_edges = list()
        for triangle in tri.simplices:
            for e1, e2 in [[0, 1], [1, 2], [2, 0]]:  # for all edges of triangle
                list_of_edges.append(less_first(triangle[e1], triangle[e2]))  # always lesser index first

        for p1, p2 in np.unique(list_of_edges, axis=0):  # remove duplicates
            i, j = key_list[p1], key_list[p2]
            i_c = tri.points[p1]
            if (0 <= i_c[0] < self.map_size[0]) and (0 <= i_c[1] < self.map_size[1]):  # only do this for nodes in the map

                j_c = tri.points[p2]

                dart = np.zeros(2, dtype=np.int8)
                for axis in range(2):
                    if j_c[axis] < 0:
                        dart[axis] = -1
                    elif j_c[axis] >= self.map_size[axis]:
                        dart[axis] = 1

                edges.append([i, j])
                coordinates.append([(int(i_c[0]+j_c[0])/2) % self.map_size[0], (int(i_c[1]+j_c[1])/2) % self.map_size[1]])
                darts.append([self.get_dart_from_coordinate(coordinates[-1], i_c), self.get_dart_from_coordinate(coordinates[-1], j_c)])

        return edges, coordinates, darts

    def clean_delaunay_graph(self):

        quads = list()
        for i, j in self.get_all_connections():  # First make the set of all double-triangle quads

            if self.types[i] == 1 and self.types[j] == 1:  # If this is a cap/cap-circle edge ignore it
                continue

            try:
                k, l = np.intersect1d(self.get_node_connections(i), self.get_node_connections(j))[:2]  # Find the 2 shared nodes and add them

                alpha = np.arccos(np.dot(self.get_unit_vector(i, k), self.get_unit_vector(j, k)))
                gamma = np.arccos(np.dot(self.get_unit_vector(i, l), self.get_unit_vector(j, l)))

                if alpha + gamma > np.pi:  # If they do not, swap the edge correctly
                    quads.append([i, j, k, l])
            except:
                print(f'GraphError: Failed to find 2 shared nodes for {i}-{j}')

        for i, j, k, l in quads:
            self.disconnect_nodes(i, j)
            self.connect_nodes(k, l)
            dart = self.get_closest_dart(k, l)
            self.darts[k, l] = dart
            self.darts[l, k] = -dart

    def spring_adjustment(self, iterations=None, ratios=None):
        if ratios is None:
            ratios = np.array((0.1, 0.5, 50), dtype=np.float32)
        if iterations is None:
            iterations = 5 * self.size
        _coordinates, _darts = _numba_spring_adjustment(self.graph, self.coordinates.astype(dtype=np.float64),
                                                        self.darts, self.weights, self.map_size, ratios,
                                                        self.get_all_connections(), iterations)
        self.coordinates, self.darts = _coordinates.astype(dtype=np.int32), _darts.astype(dtype=np.int8)

    def get_virtual_graph(self):

        virtual_size = self.size + 1
        for i, j in self.get_all_connections():
            virtual_size += np.count_nonzero(self.darts[i, j])
        virtual_size = int(virtual_size)

        virtual_graph = np.zeros((virtual_size, virtual_size), dtype=np.bool_)
        virtual_coordinates = np.zeros((virtual_size, 2), dtype=np.int32)

        for i in range(self.size):
            virtual_coordinates[i] = self.coordinates[i]

        k = len(self.coordinates)
        done_edges = set()
        for i, j in self.get_all_connections():
            if (i, j) not in done_edges:  # If we haven't done this connection continue
                done_edges.add((j, i))

                dart_x, dart_y = self.darts[i, j]

                if dart_x == 0 and dart_y == 0:  # If the connection does not cross the torus then just add the edge
                    virtual_graph[i, j] = 1
                    virtual_graph[j, i] = 1
                else:  # Otherwise we need to find the virtual coordinates
                    vector = self.get_vector(i, j)

                    infinite_coordinates = list()  # Find the infinite edge points
                    for axis in range(2):
                        if self.darts[i, j][axis] == -1:
                            ic = 0
                        elif self.darts[i, j][axis] == 1:
                            ic = self.map_size[axis]
                        else:
                            continue
                        if axis == 0:
                            infinite_coordinates.append([ic, self.coordinates[i, 1] + (ic - self.coordinates[i, 0]) * vector[1] / vector[0]])
                        else:
                            infinite_coordinates.append([self.coordinates[i, 0] + (ic - self.coordinates[i, 1]) * vector[0] / vector[1], ic])

                    if len(infinite_coordinates) == 2:  # Find which is closer and build virtual graph
                        virtual_graph[i, k] = 1  # 1st node to 1st edge
                        virtual_graph[k, i] = 1

                        virtual_graph[k+1, k+2] = 1  # 1st edge to 2nd edge
                        virtual_graph[k+2, k+1] = 1
                        if np.linalg.norm(np.subtract(self.coordinates[i], infinite_coordinates[0])) > np.linalg.norm(np.subtract(self.coordinates[i], infinite_coordinates[1])):  # seeing which is closer
                            infinite_coordinates = [infinite_coordinates[1], infinite_coordinates[0]]
                            virtual_coordinates[k+1] = [infinite_coordinates[0][0], infinite_coordinates[0][1] - dart_y * self.map_size[1]]
                            virtual_coordinates[k+2] = [infinite_coordinates[1][0], infinite_coordinates[1][1] - dart_y * self.map_size[1]]
                        else:
                            infinite_coordinates = [infinite_coordinates[0], infinite_coordinates[1]]
                            virtual_coordinates[k+1] = [infinite_coordinates[0][0] - dart_x * self.map_size[0], infinite_coordinates[0][1]]
                            virtual_coordinates[k+2] = [infinite_coordinates[1][0] - dart_x * self.map_size[0], infinite_coordinates[1][1]]
                        virtual_coordinates[k] = infinite_coordinates[0]

                        virtual_graph[k+3, j] = 1  # 2nd edge to 2nd node
                        virtual_graph[j, k+3] = 1
                        virtual_coordinates[k+3] = [infinite_coordinates[1][0] - dart_x * self.map_size[0], infinite_coordinates[1][1] - dart_y * self.map_size[1]]
                    else:
                        virtual_graph[i, k] = 1  # Vertex to edge
                        virtual_graph[k, i] = 1
                        virtual_coordinates[k] = infinite_coordinates[0]
                        virtual_graph[k+1, j] = 1  # Edge to connection
                        virtual_graph[j, k+1] = 1
                        virtual_coordinates[k+1] = [infinite_coordinates[0][0] - dart_x * self.map_size[0], infinite_coordinates[0][1] - dart_y * self.map_size[1]]

                    k += 2 * len(infinite_coordinates)

        return virtual_graph, virtual_coordinates

    def plot(self):

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()

        for i, j in self.get_all_connections():
            x1, y1 = self.coordinates[i]
            x2, y2 = self.coordinates[j] + self.darts[i, j] * self.map_size

            colour = 'k-'
            if self.planes[i] != self.planes[j]:
                colour = 'k--'

            ax.plot((x1, x2), (y1, y2), colour)

        for i, (x, y) in enumerate(self.coordinates):
            ax.plot(x, y, self.plot_colour[i])
            ax.text(x+5, y+5, s=f'{i}')

        ax.set(xlim=(0, self.map_size[0]), ylim=(0, self.map_size[1]))
        ax.set_aspect('equal')

        return ax