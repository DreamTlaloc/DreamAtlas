import numpy as np

from DreamAtlas import *


def make_virtual_graph(graph, coordinates, darts, mapsize):

    virtual_graph, virtual_coordinates = dict(), dict()
    for i in graph:
        virtual_graph[i] = list()
        virtual_coordinates[i] = coordinates[i]

    new_index = max(graph) + 1
    done_edges = {(-1, -1)}
    for i in graph:
        for j_index in range(len(graph[i])):
            j = graph[i][j_index]
            if (i, j) not in done_edges:  # If we haven't done this connection continue
                done_edges.add((j, i))
                dart_x, dart_y = darts[i][j_index]

                if dart_x == 0 and dart_y == 0:  # If the connection does not cross the torus then just add the edge
                    virtual_graph[i].append(j)
                    virtual_graph[j].append(i)
                else:                            # Otherwise we need to find the virtual coordinates
                    vector = coordinates[j] + darts[i][j_index] * np.asarray(mapsize) - coordinates[i]
                    unit_vector = vector / np.linalg.norm(vector)

                    infinite_coordinates = list()  # Find the infinite edge points
                    for axis in range(2):
                        if darts[i][j_index][axis] == -1:
                            ic = 0
                        elif darts[i][j_index][axis] == 1:
                            ic = mapsize[axis]
                        else:
                            continue
                        if axis == 0:
                            infinite_coordinates.append([ic, coordinates[i][1] + (ic - coordinates[i][0]) * unit_vector[1] / unit_vector[0]])
                        else:
                            infinite_coordinates.append([coordinates[i][0] + (ic - coordinates[i][1]) * unit_vector[0] / unit_vector[1], ic])

                    if len(infinite_coordinates) == 2:  # Find which is closer and build virtual graph
                        virtual_graph[i].append(new_index)  # 1st node to 1st edge
                        virtual_graph[new_index] = [i]
                        virtual_coordinates[new_index] = infinite_coordinates[0]

                        virtual_graph[new_index + 1] = [new_index + 2]  # 1st edge to 2nd edge
                        virtual_graph[new_index + 2] = [new_index + 1]
                        if np.linalg.norm(np.subtract(coordinates[i], infinite_coordinates[0])) > np.linalg.norm(np.subtract(coordinates[i], infinite_coordinates[1])):  # seeing which is closer
                            infinite_coordinates = [infinite_coordinates[1], infinite_coordinates[0]]
                            virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0], infinite_coordinates[0][1] - dart_y * mapsize[1]]
                            virtual_coordinates[new_index + 2] = [infinite_coordinates[1][0], infinite_coordinates[1][1] - dart_y * mapsize[1]]
                        else:
                            infinite_coordinates = [infinite_coordinates[0], infinite_coordinates[1]]
                            virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0] - dart_x * mapsize[0], infinite_coordinates[0][1]]
                            virtual_coordinates[new_index + 2] = [infinite_coordinates[1][0] - dart_x * mapsize[0], infinite_coordinates[1][1]]

                        virtual_graph[new_index + 3] = [j]  # 2nd edge to 2nd node
                        virtual_graph[j].append(new_index + 3)
                        virtual_coordinates[new_index + 3] = [infinite_coordinates[1][0] - dart_x * mapsize[0], infinite_coordinates[1][1] - dart_y * mapsize[1]]
                    else:
                        virtual_graph[i].append(new_index)  # Vertex to edge
                        virtual_graph[new_index] = [i]
                        virtual_coordinates[new_index] = infinite_coordinates[0]
                        virtual_graph[new_index + 1] = [j]  # Edge to connection
                        virtual_graph[j].append(new_index + 1)
                        virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0] - dart_x * mapsize[0], infinite_coordinates[0][1] - dart_y * mapsize[1]]

                    new_index += 2*len(infinite_coordinates)

    return virtual_graph, virtual_coordinates


def ui_find_virtual_graph(graph, coordinates, map_size, wraparound):

    darts = dict()
    for i in graph:
        darts[i] = list()
        ix, iy = coordinates[i]
        for j in graph[i]:
            min_dist = np.inf
            best_dart = [0, 0]
            for n in wraparound:
                jx, jy = np.add(coordinates[j], np.multiply(map_size, n))
                new_dist = np.linalg.norm([ix-jx, iy-jy])
                if new_dist < min_dist:
                    best_dart = n
                    min_dist = new_dist
            darts[i].append(best_dart)

    return make_virtual_graph(graph, coordinates, darts, map_size)
