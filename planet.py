#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """
        self.paths = {} 
    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        start_cordinates = start[0]
        start_direction = start[1]
        target_cordinates = target[0]
        target_direction = target[1]

        if start_cordinates in self.paths.keys():
            self.paths[start_cordinates][start_direction] = (
                target_cordinates, target_direction, weight)
        else: 
            self.paths[start_cordinates] = {start_direction: (
                target_cordinates, target_direction, weight)}

        if target_cordinates in self.paths.keys():
            self.paths[target_cordinates][target_direction] = (
                start_cordinates, start_direction, weight)
        else:
            self.paths[target_cordinates] = {target_direction: (
                start_cordinates, start_direction, weight)}

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths 

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        return self.paths

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        # First we need to transform our dictionary into a wieghted adjecency matrix
        number_of_nodes = len(self.paths.keys())

        # Initiate a new graph class with the size of the number of nodes and pass the dictionary to render the matrix
        graph = Graph(self.paths, start=start, target=target)

        # Return the path as a list of paths
        return graph.dijkstra()

class Graph:
    """ Graph is a helper class used to create a adjecency matrix and use it in the dijkstra algorithm"""
    
    # Max int to act as infinity in the dijkstra algorithm
    max_int = 999999
    def __init__(self, dictionary, start, target):
        # Get the vertices
        self.vertices = dictionary.keys()
        self.vertices_with_paths = dictionary

        # Target and starting vertex
        self.start = start
        self.target = target

        # Number of vertices
        self.size = len(self.vertices)

        # Size the matrix accordingly 
        self.adjMatrix = []
        for i in range(self.size):
            self.adjMatrix.append([0 for i in range(self.size)])
        

        # Generate a matrix from the planet dictionary
        self.dict_to_matrix(dictionary)

    def add_edge(self, v1, v2, weight):
        # Add edge to the adjecency matrix
        if v1 == v2:
            pass
        self.adjMatrix[v1][v2] = weight
        self.adjMatrix[v2][v1] = weight

    def print_matrix(self):
        # A helper function for printing the adjecency matrix
        for row in self.adjMatrix:
            print(" ".join([str(val).ljust(3) for val in row]))

    def dict_to_matrix(self, dictionary):
        # Generate the nodes list based on the passed in dictionary keys
        nodes = list(dictionary.keys())
        node_indices = {node: i for i, node in enumerate(nodes)}
        for node, edges in dictionary.items():
            for direction, edge in edges.items():
                target_node, target_direction, weight = edge
                if weight == -1:
                    weight = self.max_int
                self.add_edge(node_indices[node],
                              node_indices[target_node], weight)

        return self.adjMatrix

    def print_dict(self):
        for key in self.vertices_with_paths:
            print(f"Vertex {key} \t", self.vertices_with_paths[key], "\n")

    def printSolution(self, dist):
        # A helper function for printing the distances 
        print ("Vertex \tDistance from Source")
        i = 0
        for node in self.vertices:
            print (node, "\t", dist[i])
            i += 1

    def get_index(self, target):
        # Dijkstra needs the node to be an integer but for better readability of the path we need it to remain a coordinate tuple
        i = 0
        for node in self.vertices:
            if(node == target):
                return i
            else:
                i += 1

    def min_distance(self, distance, shortest_path_arr):
        min_distance = self.max_int

        try:
            for i in range(self.size):
                if distance[i] < min_distance and shortest_path_arr[i] == False or distance[i] == min_distance and shortest_path_arr[i] == False :
                    min_distance = distance[i]
                    min_index = i
            
            return min_index
        
        except UnboundLocalError:
            return None

    def dijkstra(self):
        starting_index = self.get_index(self.start)
        distance = [self.max_int] * self.size
        distance[starting_index] = 0
        shortest_path_arr = [False] * self.size

        # Parent array for storing the path
        parent = [-1] * self.size
        for vertex in range(self.size):
            x = self.min_distance(distance, shortest_path_arr)
            if x == None:
                return None
            
            shortest_path_arr[x] = True

            for i in range(self.size):
                if self.adjMatrix[x][i] > 0 and shortest_path_arr[i] == False and distance[i] > distance[x] + self.adjMatrix[x][i]:
                    distance[i] = distance[x] + self.adjMatrix[x][i]
                    parent[i] = x

        # Get the shorthest path as a ordered list of coordtinates
        shortest_path = {}
        for node in range(self.size):
            path = []
            curr = node
            while curr != -1:
                path.insert(0, list(self.vertices)[curr])
                curr = parent[curr]
            shortest_path[list(self.vertices)[node]] = path
        
        # Return only the desired path to the predefined target, not all the paths
        try:
            if self.start not in shortest_path[self.target]:
                return None
        except KeyError:
            return None
        
        shortest_path_with_directions = []
        
        # Get not only the nodes but also the directions
        for i, node in enumerate(shortest_path[self.target]):
            small_start = shortest_path[self.target][i]
            try:
                small_target = shortest_path[self.target][i + 1]
            except IndexError:
                break
            for direction in self.vertices_with_paths[small_start]:
                if self.vertices_with_paths[small_start][direction][0] == small_target:
                    shortest_path_with_directions.append(((small_start), int(direction))) 
        
        return shortest_path_with_directions

