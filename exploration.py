import ev3dev.ev3 as ev3
import json

from communication import Communication
from planet import Planet
from odometry import Odometry

import time


class Exploration:
    def __init__(self, client, logger):
        """Initiates the exploration module and all the sensors, motors"""

        # Planet and communication refrence from main
        self.planet = Planet()
        self.coms = Communication(client, logger)

        self.coms.client_test_planet("Anin")

        # Sensors configuration
        self.left = ev3.LargeMotor("outD")
        self.right = ev3.LargeMotor("outB")
        self.cs = ev3.ColorSensor("in3")
        self.us = ev3.UltrasonicSensor("in4")
        self.ts = ev3.TouchSensor()
        self.sound = ev3.Sound()
        self.correction_factor1 = 100/250
        self.offset = 250
        self.speed = 200  # Optimal 130
        self.lastError = 0
        self.derivate = 0
        self.rgb_list_sum = []

        # Color configuration
        self.red = []
        self.blue = []
        self.black = 0
        self.white = 0

        # Planet info
        self.planetName = None
        self.startDirection = 0
        self.startX = 0
        self.startY = 0

        self.endX = 0
        self.endY = 0
        self.endDirection = 0
        self.currently_facing = 0

        # Path info and DFS stack
        self.available_paths_stack = []
        self.going_back_to_a_node = False
        self.last_path_was_blocked = False

        # A list to track traversed nodes
        self.traversed = []
        self.backtracking_to = None

        # Target info
        self.path_to_target = []
        self.targetX = None
        self.targetY = None
        self.going_to_target = False

        # Was the first station reached
        self.first_planet_reached = False

        # Odometry list of values
        self.r = []
        self.l = []
        
    def color_sensor(self):
        """Returns the list of currently messured colors"""
        self.cs.mode = "RGB-RAW"
        rgb_list = self.cs.bin_data("hhhh")

        return rgb_list

    def calibrate_colors(self, new_calibration):
        """Scan white, black, red and blue in order to update the values based on current light in the room"""
        if new_calibration:
            print("Get white")
            input()
            self.white = sum(self.color_sensor()) / 3
            print(self.white)

            print("Get black")
            input()
            self.black = sum(self.color_sensor()) / 3
            print(self.black)

            print("Get red")
            input()
            self.red = self.color_sensor()
            print(self.red)

            print("Get blue")
            input()
            self.blue = self.color_sensor()
            print(self.blue)

            print("Ready")
            input()

        else:
            self.white = 411.3333333333333
            self.black = 243.33333333333334
            self.red = (94, 31, 9, 655)
            self.blue = (12, 85, 68, 656)

    def explore(self):
        """The main function for the whole exploration"""
        self.left.reset()
        self.right.reset()
        self.left.stop_action = "brake"
        self.right.stop_action = "brake"
        self.us.mode = 'US-DIST-CM'

        self.offset = self.white + self.black

        self.offset = self.offset / 2

        while True:
            # Stop panic button
            if self.ts.value() == 1:
                self.stop()
                break            
            
            # Station and all the traverse
            if self.is_station():
                if not self.first_planet_reached:
                    # On reaching the first planet
                    self.first_planet_reached = True
                    self.stop()
                    planet_info = self.coms.client_ready()
                    self.planetName = planet_info[0]
                    self.startX = planet_info[1]
                    self.startY = planet_info[2]
                    self.startDirection = planet_info[3]

                    # Initialize the odometry module
                    odo = Odometry(12, self.startX, self.startY, self.startDirection, self.r, self.l)
                    self.r = []
                    self.l = []

                    time.sleep(2)

                    # Add the initialy traversed path to logged paths
                    direction_to_log = (self.startDirection - 180) % 360
                    self.traversed.append([(self.startX, self.startY), direction_to_log])
                    print("[traversed][start] appended this path to already traversed", [(self.startX, self.startY), direction_to_log])

                    # Increase the depth for DFS
                    scanned_paths_directions = self.scan_paths(
                        self.startDirection)

                    self.currently_facing = self.startDirection

                    # Add scanned paths to avilable paths
                    for direction in scanned_paths_directions:
                        self.available_paths_stack.insert(
                            0, [(self.startX, self.startY), (direction) % 360])


                else:
                    # Report to the mothership about a completed path and await correction
                    self.stop()

                    # Pop the currently driven path from the stack
                    self.available_paths_stack = list(filter(([(self.startX, self.startY), self.startDirection]).__ne__, self.available_paths_stack))
                    

                    if self.last_path_was_blocked:
                        self.last_path_was_blocked = False
                        self.endX = self.startX
                        self.endY = self.startY
                        self.endDirection = self.startDirection
                        path_status = "blocked"

                        newX = self.startX
                        newY = self.startY
                        newDirection = self.startDirection
                    else:
                        odo = Odometry(12, self.startX, self.startY, self.startDirection, self.r, self.l)
                        odo.delta_rotation()
                        newX, newY, newDirection = odo.convert_new_postion()
                        newDirection = (newDirection - 180) % 360
                        newX, newY, newDirection = odo.round_cordinates(newX, newY, newDirection)
                        path_status = "free"

                    self.r = []
                    self.l = []

                    time.sleep(2)

                    path_correction = self.coms.client_path(
                        [self.startX, self.startY, self.startDirection, newX, newY, newDirection, path_status])
                    self.startX, self.startY, self.startDirection, self.endX, self.endY, self.endDirection, status, weight = path_correction

                    if not (self.going_back_to_a_node or self.going_to_target):
                        self.planet.add_path(((self.startX, self.startY), self.startDirection), ((
                            self.endX, self.endY), self.endDirection), weight)


                    # If on target coordinates
                    if(self.targetX == self.endX and self.targetY == self.endY):
                        self.coms.client_target_reached()
                        break
                    
                    print("Self backtracking and current cordinates", self.backtracking_to, (self.endX, self.endY))
                    if self.backtracking_to == (self.endX, self.endY):
                        self.backtracking_to = None
                        print(" \n Not going to node anymore \n")
                        self.going_back_to_a_node = False

                    # If on a already scanned node, do not rescan
                    if (self.endX, self.endY) not in self.get_traversed_nodes():
                        # Increase the depth for DFS
                        scanned_paths_directions = self.scan_paths(
                            self.endDirection + 180)
                        
                        # Add scanned paths to avilable paths
                        for direction in scanned_paths_directions:
                            if self.going_back_to_a_node or self.going_to_target:
                                self.available_paths_stack.append([(self.endX, self.endY), (direction) % 360])
                            else:
                                self.available_paths_stack.insert(
                                    0, [(self.endX, self.endY), (direction) % 360])
                    
                    else:
                        # Move a couple cm forward to get off the station
                        self.turn(6)
                        self.right.position_sp = 150
                        self.left.position_sp = 150
                        self.right.speed_sp = 100
                        self.left.speed_sp = 100
                        self.right.command = "run-to-rel-pos"
                        self.left.command = "run-to-rel-pos"
                        self.right.wait_until_not_moving()

                    # Add target path
                    if self.coms.target_avilable() and not self.going_to_target:
                        self.targetX, self.targetY = self.coms.get_target()
                        print("Target found at ", self.targetX, self.targetY)
                        self.path_to_target = self.planet.shortest_path((self.endX, self.endY), (self.targetX, self.targetY))
                        if self.path_to_target != None:
                            self.going_to_target = True
                            print(self.path_to_target)
                            self.path_to_target.reverse()
                            for node in self.path_to_target:
                                self.available_paths_stack.insert(0, [(node[0][0], node[0][1]), node[1]])
                        else:
                            print("There is no path to target, explore further")


                    # Starting path
                    self.traversed.append([(self.startX, self.startY), self.startDirection])

                    # Ending path
                    self.traversed.append([(self.endX, self.endY), self.endDirection])

                    # Modify the variables for further traversal
                    self.startX = self.endX
                    self.startY = self.endY

                    # Inform the robot about current direction
                    self.currently_facing = (self.endDirection + 180) % 360

                    # Check wheather there are paths unveiled
                    if self.coms.is_pathUnveiled:
                        for path in self.coms.unvailedPaths:
                            startX, startY, startDirection, endX, endY, endDirection, pathStatus, weight = path
                            self.planet.add_path(
                                ((startX, startY), startDirection), ((endX, endY), endDirection), weight)

                # Choose a new path using DFS
                next_path_info = self.path_selection(
                    (self.startX, self.startY))
                
                if next_path_info == None:
                    print("No more paths to explore")
                    self.coms.client_exploration_target_reached()
                    break

                self.startX = next_path_info[0][0]
                self.startY = next_path_info[0][1]
                the_rotation = (
                    next_path_info[1] - self.currently_facing) % 360

                # If the server corrects the chosen direction, make it relative to current position
                self.startDirection = self.coms.client_path_select(
                    [self.startX, self.startY, (next_path_info[1]) % 360])
                if self.startDirection != next_path_info[1]:
                    print("Server changed the direction!")

                    # Add the deleted path back to the stack if the server says so...
                    self.available_paths_stack.insert(0, [(self.startX, self.startY), self.startDirection])
                    the_rotation = (self.startDirection -
                                    self.currently_facing) % 360
                
                self.turn(the_rotation)
                self.entry_scan()

            # If there is no obstacle or other station follow the line
            if not self.obstacle(self.us.value()):
                self.line_following()

            # If there is an obstacle, avoid it
            else:
                self.turn(180)
                # For odometry
                self.r.reverse()
                self.l.reverse()
                # Report a blocked path and add it to the map
                
                self.last_path_was_blocked = True
                print("[blocked] the path from these coordinates is blocked", [(self.startX, self.startY), self.startDirection])
                self.entry_scan()

    def path_selection(self, current_location):
        # Selects the path based on DFS and other factors 
        all_paths = self.planet.get_paths()
        while True:
            try:
                path_select = self.available_paths_stack[0]
            except IndexError:
                return None
            
            try:
                available_paths = all_paths[path_select[0]]
                print(available_paths)
                if path_select in self.traversed and \
                    not (self.going_to_target or self.going_back_to_a_node):
                    print("This path was already traversed", path_select)
                    self.available_paths_stack.pop(0)
                    continue

                if not (self.going_to_target or self.going_back_to_a_node):
                    to_break = False
                    for direction in available_paths:
                        if direction == path_select[1]:
                            print("This path was already traversed or unvailed", path_select)
                            self.available_paths_stack.pop(0)
                            to_break = True
                            break
                    if to_break:
                        continue
            except Exception as e:
                pass
            
            # Backtrack if there are not other avaiable paths on the current node
            if path_select[0] != current_location and not self.going_back_to_a_node:
                print("Selected path is not in the current coordinates. Coordinates, path", current_location, path_select)
                path_to_backtrack = self.planet.shortest_path(current_location, path_select[0])
                if path_to_backtrack != None:
                    print("Going back to previous node")
                    self.backtracking_to = path_select[0]
                    print("Backtracking to", self.backtracking_to)
                    path_to_backtrack.reverse()
                    print(path_to_backtrack)
                    for node in path_to_backtrack:
                        ("Inserted", [(node[0][0], node[0][1]), node[1]])
                        self.available_paths_stack.insert(0, [(node[0][0], node[0][1]), node[1]])
                    self.going_back_to_a_node = True
                    continue
                else:
                    print("[path select shorthest path] There is no path to previous node!")

            # Ignore a selected path if we know that it is blocked
            if path_select not in self.traversed:
                try:
                    if all_paths[current_location][path_select[1]][2] == -1 and current_location == path_select[0]:
                        print("Selected path", path_select)
                        print("This path is blocked!")
                        self.available_paths_stack.remove(path_select)
                        continue
                except KeyError:
                    pass
            break
        print("Finally selected path", path_select)
        return path_select

    def get_traversed_nodes(self):
        nodes = []
        for path in self.traversed:
            nodes.append(path[0])
        
        return nodes


    def is_station(self):
        """Checks weather the color under the sensor is blue or red"""
        if self.color_sensor()[0] > self.red[0] - 15 and self.color_sensor()[0] < self.red[0] + 15 \
                and self.color_sensor()[1] > self.red[1] - 15 and self.color_sensor()[1] < self.red[1] + 15 \
                and self.color_sensor()[2] > self.red[2] - 15 and self.color_sensor()[2] < self.red[2] + 15 or \
                self.color_sensor()[0] > self.blue[0] - 15 and self.color_sensor()[0] < self.blue[0] + 15 \
                and self.color_sensor()[1] > self.blue[1] - 15 and self.color_sensor()[1] < self.blue[1] + 15 \
                and self.color_sensor()[2] > self.blue[2] - 15 and self.color_sensor()[2] < self.blue[2] + 15:
            return True
        else:
            return False

    def line_following(self):
        """Function for line following"""
        rgb = self.color_sensor()
        self.rgb_list_sum = rgb[0] + rgb[1] + rgb[2]

        error = self.rgb_list_sum-self.offset
        self.derivate = error - self.lastError
        turn = self.correction_factor1*error + self.derivate*self.correction_factor1

        self.left.speed_sp = self.speed + turn
        self.left.command = "run-forever"

        self.right.speed_sp = self.speed-turn
        self.right.command = "run-forever"
        self.lastError = error

        self.r.append(self.right.position)
        self.l.append(self.left.position)

    def scan_paths(self, current_direction):
        # Set up
        # Correct position to be more balanced
        self.turn(6)

        # Move a couple cm forward to reach all nodes
        self.right.position_sp = 150
        self.left.position_sp = 150
        self.right.speed_sp = 100
        self.left.speed_sp = 100
        self.right.command = "run-to-rel-pos"
        self.left.command = "run-to-rel-pos"
        self.right.wait_until_not_moving()
        # Scanning
        directions_of_paths = []
        self.turn(-135)
        # Scan every 90 degeers
        left = self.scan_quarter()  # current_direction + 270
        middle = self.scan_quarter()  # current_direction + 0
        right = self.scan_quarter()  # current_driection + 90

        if left:
            left = current_direction + 270
            if left >= 360:
                left -= 360
                directions_of_paths.append(left)
            else:
                directions_of_paths.append(left)
        if middle:
            middle = current_direction + 0
            if middle >= 360:
                middle -= 360
                directions_of_paths.append(middle)
            else:
                directions_of_paths.append(middle)

        if right:
            right = current_direction + 90
            if right >= 360:
                right -= 360
                directions_of_paths.append(right)
            else:
                directions_of_paths.append(right)

        self.turn(-135)
        return directions_of_paths

    def scan_quarter(self):
        """Scan every 90 degrees and return a list of direction with a path"""
        there_is_a_path = False
        self.right.position_sp = -180  # in reality 90 degrees
        self.left.position_sp = 180  # in reality 90 degrees

        self.right.speed_sp = 90
        self.left.speed_sp = 90

        self.right.command = "run-to-rel-pos"
        self.left.command = "run-to-rel-pos"

        while True:
            time.sleep(0.1)
            try:
                if (self.right.state[0] == "running"):
                    if (sum(self.color_sensor()) <= self.black * 3 + 50):
                        there_is_a_path = True
                else:
                    print(self.right.state)
                    break
            except IndexError:
                break
        return there_is_a_path

    def set_on_black(self):
        """Rotate until black path is found under the sensor"""
        self.right.reset()
        self.left.reset()
        while True:
            self.right.position_sp = -2  # Erlier 4
            self.left.position_sp = 2  # Erlier 4
            self.right.speed_sp = 50
            self.left.speed_sp = -50
            self.right.command = "run-to-rel-pos"
            self.left.command = "run-to-rel-pos"

            if (self.ts.value() == 1):
                break

            # Break on black
            if (sum(self.color_sensor()) <= self.black * 3 + 50):
                return self.left.position

    def entry_scan(self):
        """Performed after every major operation in order to locate the black line and eliminate all the potential errors"""
        self.right.position_sp = 45 * 2
        self.left.position_sp = -45 * 2
        self.right.speed_sp = 200
        self.left.speed_sp = 200
        self.right.command = "run-to-rel-pos"
        self.left.command = "run-to-rel-pos"

        self.right.wait_until_not_moving()

        self.set_on_black()

    def stop(self):
        """Stops the motors"""
        self.right.stop()
        self.left.stop()

    def obstacle(self, distance):
        """Checks if there is and obstacle in sight"""
        if (distance < 60):
            self.stop()
            self.sound.speak("Obstacle detected")
            return True
        return False

    def turn(self, arc):
        """Turn to the given arc, -arc for left +arc for right"""
        if arc != 0:
            self.right.reset()
            self.left.reset()
            self.right.position_sp = -arc * 2
            self.left.position_sp = arc * 2

            self.right.speed_sp = 90
            self.left.speed_sp = 90

            self.right.command = "run-to-rel-pos"
            self.left.command = "run-to-rel-pos"
            self.right.wait_until_not_moving()
