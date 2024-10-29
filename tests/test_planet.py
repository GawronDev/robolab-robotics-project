#!/usr/bin/env python3

import unittest
from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH),
                             ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST),
                             ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        #chadwick5
        self.maxDiff=None
        self.planet = Planet()
        self.planet.add_path(((1, 10), Direction.NORTH), ((1, 12), Direction.SOUTH), 9)   
        self.planet.add_path(((1, 12), Direction.NORTH), ((1, 13), Direction.SOUTH), 12)
        self.planet.add_path(((1, 12), Direction.WEST), ((0, 12), Direction.EAST), 6)
        self.planet.add_path(((0, 12), Direction.NORTH), ((1, 13), Direction.WEST), 6)
        self.planet.add_path(((0, 12), Direction.SOUTH), ((0, 11), Direction.NORTH), 7)
        self.planet.add_path(((0, 11), Direction.SOUTH), ((-1, 10), Direction.EAST), 1)
        self.planet.add_path(((-1, 10), Direction.NORTH), ((-1, 11), Direction.SOUTH), 8)
        self.planet.add_path(((-1, 11), Direction.EAST), ((0, 11), Direction.WEST), 3)
        self.planet.add_path(((-1, 11), Direction.NORTH), ((-1, 12), Direction.SOUTH), 1)
        self.planet.add_path(((-1, 12), Direction.EAST), ((0, 12), Direction.WEST), 5)
        self.planet.add_path(((-1, 12), Direction.NORTH), ((0, 14), Direction.WEST), -1)
        self.planet.add_path(((0, 14), Direction.SOUTH), ((0, 14), Direction.SOUTH), 1)
        self.planet.add_path(((0, 14), Direction.EAST), ((1, 13), Direction.NORTH), -1)
        


    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        
        path=self.planet.get_paths() 
        muster={
            (1,10):{
            Direction.NORTH:((1, 12), Direction.SOUTH, 9)
            },
            (1,12):{
            Direction.SOUTH:((1, 10), Direction.NORTH, 9),
            Direction.NORTH:((1, 13), Direction.SOUTH, 12),
            Direction.WEST:((0, 12), Direction.EAST, 6)
            },
            (1,13):{
            Direction.SOUTH:((1, 12), Direction.NORTH, 12),
            Direction.WEST:((0, 12), Direction.NORTH, 6),
            Direction.NORTH:((0, 14), Direction.EAST, -1),
            },
            (0,12):{
            Direction.EAST:((1, 12), Direction.WEST, 6),
            Direction.NORTH:((1, 13), Direction.WEST, 6),
            Direction.SOUTH:((0, 11), Direction.NORTH, 7),
            Direction.WEST:((-1, 12), Direction.EAST, 5)
            },
            (0,11):{
            Direction.NORTH:((0, 12), Direction.SOUTH, 7),
            Direction.SOUTH:((-1, 10), Direction.EAST, 1),
            Direction.WEST:((-1, 11), Direction.EAST, 3)
            },
            (-1,10):{
            Direction.EAST:((0, 11), Direction.SOUTH, 1),
            Direction.NORTH:((-1, 11), Direction.SOUTH, 8)
            },
            (-1,11):{
            Direction.SOUTH:((-1, 10), Direction.NORTH, 8),
            Direction.EAST:((0, 11), Direction.WEST, 3),
            Direction.NORTH:((-1, 12), Direction.SOUTH, 1)
            },
            (-1,12):{
            Direction.SOUTH:((-1, 11), Direction.NORTH, 1),
            Direction.EAST:((0, 12), Direction.WEST, 5),
            Direction.NORTH:((0, 14), Direction.WEST, -1)
            },
            (0,14):{
            Direction.WEST:((-1, 12), Direction.NORTH, -1),
            Direction.SOUTH:((0, 14), Direction.SOUTH, 1),
            Direction.SOUTH:((0, 14), Direction.SOUTH, 1),
            Direction.EAST:((1, 13), Direction.NORTH, -1)
            }
        }
        self.assertEqual(path, muster)
        
    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        planet=Planet()
        path=planet.get_paths()
        self.assertEqual(path , {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        #a=self.planet.shortest_path((1,10),(1,13)) 
        
        #c=[(1,10), (1,12), (1,13)]
        
        #self.assertEqual(c,a)    
        print(self.planet.shortest_path((1,12),(0,11)))
    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        a=self.planet.shortest_path((0,12),(0,14))
        self.assertIsNone(a)

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        a=self.planet.shortest_path((1,10),(1,13))
        b=[(1,10), (1,12), (1,13)]
        self.assertEqual(a,b)

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 12), (-1, 11)))

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0,12), (0, 15)))


if __name__ == "__main__":
    unittest.main()
