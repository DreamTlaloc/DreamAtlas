from DreamAtlas import *


def embed_region_graph(graph: dict,
                       map_size: np.array,
                       scale_down: int,
                       seed: int):

    graph_range = range(1, 1 + len(graph))

    # Set the graph size to embed (smaller is faster)
    size = np.array(map_size / scale_down, dtype=np.uint32)
    connections = [[1, 0], [0, 1], [0, -1], [-1, 0]]

    # Make the H graph
    target_graph = dict()
    for x in range(size[0]):
        for y in range(size[1]):
            target_graph[(int(x * scale_down), int(y * scale_down))] = list()
            for connection in connections:
                x_coord = int(((x + connection[0]) % size[0]) * scale_down)
                y_coord = int(((y + connection[1]) % size[1]) * scale_down)
                target_graph[(int(x * scale_down), int(y * scale_down))].append((x_coord, y_coord))

    target_graph = ntx.Graph(incoming_graph_data=target_graph)
    while True:
        initial_embedding, worked = mnm.find_embedding(ntx.Graph(incoming_graph_data=graph), target_graph, return_overlap=True, random_seed=seed)
        if worked:
            break
        else:
            seed = rd.randint(0, 100000)
            print('\033[31mEmbedding failed: Trying with new seed (%i)\x1b[0m' % seed)

    # Form the subgraph of the target graph
    subgraph_nodes, node_2_index = list(), dict()
    for i in graph_range:
        for node in initial_embedding[i]:
            node_2_index[node] = i
            subgraph_nodes.append(node)
    subgraph = target_graph.subgraph(subgraph_nodes)

    # Build the graph for attractor adjustment
    attractor_graph, attractor_coordinates, attractor_darts, done_edges = dict(), dict(), dict(), set()
    for i in graph_range:
        for node in initial_embedding[i]:  # Loop over all the embedded nodes
            attractor_graph[node] = []
            attractor_coordinates[node] = [node[0], node[1]]
            attractor_darts[node] = []

            for edge in ntx.edges(subgraph, node):  # Add the connected nodes and darts
                j = node_2_index[edge[1]]
                if j == i or j in graph[i]:
                    dart = [0, 0]
                    for axis in range(2):
                        if abs(edge[0][axis] - edge[1][axis]) > scale_down:
                            dart[axis] = np.sign(edge[0][axis] - edge[1][axis])
                    attractor_graph[node].append(edge[1])
                    attractor_darts[node].append(dart)

    attractor_coordinates, attractor_darts = attractor_adjustment(attractor_graph, attractor_coordinates, attractor_darts, node_2_index, map_size, damping_ratio=0.5, iterations=1000)

    coordinates, darts, done_edges = dict(), dict(), set()
    for i in graph:  # Merge the alike vertices of the graph
        coordinate_sum = 0
        coordinates_offset = np.subtract(np.divide(map_size, 2), attractor_coordinates[initial_embedding[i][0]])
        for node in initial_embedding[i]:  # Loop over all the nodes for this vertex
            coordinate_sum += np.mod(np.add(coordinates_offset, attractor_coordinates[node]), map_size)
        coordinates[i] = np.mod(np.subtract(np.divide(coordinate_sum, len(initial_embedding[i])), coordinates_offset), map_size)

    for i in graph:  # Make final darts
        darts[i] = []
        for j in graph[i]:
            dart_candidates = []
            for node1 in initial_embedding[i]:
                for node2 in initial_embedding[j]:
                    if node2 in attractor_graph[node1]:
                        dart = attractor_darts[node1][attractor_graph[node1].index(node2)]
                        dart_candidates.append(dart)
            darts[i].append(dart)

    return coordinates, darts


@njit(parallel=True)
def _numba_attractor_adjustment(key_list: np.array,
                                graph: np.array,
                                coordinates: np.array,
                                darts: np.array,
                                attractor_array: np.array,
                                damping_ratio: float,
                                map_size: np.array,
                                iterations: int):
    dict_size = len(key_list)

    net_velocity = np.zeros((dict_size, 2))
    for _ in range(iterations):
        attractor_force = np.zeros((dict_size, 2))
        for i in prange(dict_size):
            for j in range(dict_size):
                if attractor_array[i, j]:
                    attractor_force[i] += coordinates[j] + darts[i, j] * map_size - coordinates[i]

        net_velocity = damping_ratio * (net_velocity + attractor_force)

        equilibrium = 1
        for c in range(dict_size):  # Check if particles are within tolerance
            if np.linalg.norm(net_velocity[c]) > 0.001:
                equilibrium = 0
                break

        coordinates += net_velocity
        for a in range(dict_size):  # Update the position
            for axis in range(2):
                if not (0 <= coordinates[a, axis] < map_size[axis]):
                    dart_change = -np.sign(coordinates[a, axis])
                    # print(dart_change, coordinates[a, axis], coordinates[a, axis] % map_size[axis])
                    coordinates[a, axis] = coordinates[a, axis] % map_size[axis]

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


def attractor_adjustment(graph: dict,
                         coordinates: dict,
                         darts: dict,
                         node_2_index: dict,
                         map_size: tuple[int, int],
                         damping_ratio: float,
                         iterations: int):

    key_list = np.zeros(len(graph), dtype=int)
    graph_array = np.zeros((len(graph), len(graph)), dtype=np.bool_)
    coordinates_array = np.zeros((len(graph), 2), dtype=np.float32)
    darts_array = np.zeros((len(graph), len(graph), 2), dtype=np.int8)
    attractor_array = np.zeros((len(graph), len(graph)), dtype=np.bool_)

    ref_2_node, node_2_ref = dict(), dict()
    index = 0
    for node in node_2_index:
        ref_2_node[index] = node
        node_2_ref[node] = index
        index += 1

    index = 0
    for i in graph:
        key_list[index] = node_2_ref[i]
        coordinates_array[index] = coordinates[i]

        index2 = 0
        for j in graph:
            if j in graph[i]:
                ji = graph[i].index(j)
                graph_array[index, index2] = 1
                darts_array[index, index2] = darts[i][ji]
                if node_2_index[j] == node_2_index[i]:
                    attractor_array[index, index2] = 1
            else:
                graph_array[index, index2] = 0
                darts_array[index, index2] = [0, 0]
            index2 += 1
        index += 1

    _coordinates, _darts = _numba_attractor_adjustment(key_list, graph_array, coordinates_array, darts_array, attractor_array, damping_ratio, map_size, iterations)
    coordinates_output, darts_output = dict(), dict()

    for i in range(len(key_list)):
        node = ref_2_node[key_list[i]]
        coordinates_output[node] = _coordinates[i].astype(np.float32).tolist()
        darts_output[node] = [None] * len(graph[node])
        for j in range(len(key_list)):
            if graph_array[i, j]:
                darts_output[node][graph[node].index(ref_2_node[key_list[j]])] = _darts[i, j].astype(np.int8).tolist()

    return coordinates_output, darts_output

