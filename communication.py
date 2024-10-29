#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
from time import sleep

# Colors for easier debugging
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        self.client.on_connect = self.on_connect_handler
        # Add your client setup here

        # Client setup
        self.client.username_pw_set('', password='') # Empty for security reasons

        # Connect to the mother ship
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)

        # Subscribe to the topic to recieve the messages
        self.client.subscribe('explorer/007', qos=2)

        # Loop start for listening to incoming messages
        self.client.loop_start()

        # Data that will be return by the server upon request
        self.planetName = None
        self.startX = 0
        self.startY = 0
        self.startOrientation = 0
        self.startDirection = 0
        self.endX = 0
        self.endY = 0
        self.endDirection = 0
        self.pathStatus = None
        self.pathWeight = 0
        self.targetX = 0
        self.targetY = 0
        self.direction_changed = False
        
        # Set to true if there is a target
        self.is_target = False

        # Set to true if a new path has been revealed
        self.is_pathUnveiled = False
        self.unvailedPaths = []

        self.logger = logger

    def on_connect_handler(self, client, data, flags, rc):
        print(WARNING + "[mqtt]" + ENDC + OKCYAN +
              "[connection]" + ENDC + " connected to mqtt")

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        # Stripping down payload to get what type of message we recieved

        # 'from' value should be 'server' as it is the mothership that sends out the messages

        # Generic message for refrence
        """
        {
        "from": "debug",
        "type": "error",
        "payload": {
            "message": "JSON provided via MQTT is not valid"
        }
        }
        """

        # Message types: error, testPlanet, notice, ready, planet,
        # path, pathSelect, pathUnveiled, target, targetReached,
        # explorationCompleted, done,

        # Take different actions based on the type of message
        if (str(payload["from"]) == "client"):
            # Debugging for the client messages
            if (str(payload["type"]) == "testPlanet"):
                print(OKBLUE + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]["planetName"]) + "\n")

            elif (str(payload["type"]) == "ready"):
                print(OKBLUE + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + "client is ready" + "\n")
                
            elif (str(payload["type"]) == "pathSelect"):
                print(OKBLUE + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

        elif (str(payload["from"]) == "server"):
            # Debugging for the server messages
            if (str(payload["type"]) == "notice"):
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")
            elif (str(payload["type"]) == "planet"):
                # Save the data from the message to return when requested
                payload_m = payload["payload"]
                self.planetName = payload_m["planetName"]
                self.startX = payload_m["startX"]
                self.startY = payload_m["startY"]
                self.startOrientation = payload_m["startOrientation"]

                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "path"):
                payload_m = payload["payload"]
                self.startX = payload_m["startX"]
                self.startY = payload_m["startY"]
                self.startDirection = payload_m["startDirection"]
                self.endX = payload_m["endX"]
                self.endY = payload_m["endY"]
                self.endDirection = payload_m["endDirection"]
                self.pathStatus = payload_m["pathStatus"]
                self.pathWeight = payload_m["pathWeight"]

                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "done"):
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "explorationComplete"):
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "targetReached"):
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "pathSelect"):
                payload_m = payload["payload"]
                self.startDirection = payload_m["startDirection"]

                self.direction_changed = True

                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "pathUnveiled"):
                payload_m = payload["payload"]
                startX = payload_m["startX"]
                startY = payload_m["startY"]
                startDirection = payload_m["startDirection"]
                endX = payload_m["endX"]
                endY = payload_m["endY"]
                endDirection = payload_m["endDirection"]
                pathStatus = payload_m["pathStatus"]
                pathWeight = payload_m["pathWeight"]

                self.unvailedPaths.append([startX, startY, startDirection, endX, endY, endDirection, pathStatus, pathWeight])
                self.is_pathUnveiled = True
                
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")

            elif (str(payload["type"]) == "target"):
                payload_m = payload["payload"]
                self.targetX = payload_m["targetX"]
                self.targetY = payload_m["targetY"]
                self.is_target = True
                
                print(OKGREEN + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + "Server marked a target at " + str(self.targetX) + " " + str(self.targetY) + "\n")

        elif (str(payload["from"]) == "debug"):
            # Debugging for the debug messages
            if (str(payload["type"]) == "error"):
                print(WARNING + "[" + str(payload["from"]) + "]" + ENDC + FAIL + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")
            else:
                print(WARNING + "[" + str(payload["from"]) + "]" + ENDC + OKCYAN + "[" + str(
                    payload["type"]) + "]" + ENDC + " " + str(payload["payload"]) + "\n")
        else:
            # Unknown message type
            print(FAIL + "MESSAGE NOT RECOGINIZED" + ENDC + " | " + payload + "\n")

    def get_planet_info(self):
        # Returns the planet info send by the mothership upon request
        return [self.planetName, self.startX, self.startY, self.startOrientation]

        # Returns the path info send by the mothership upon request
    def get_path_info(self):
        return [self.startX, self.startY, self.startDirection, self.endX, self.endY, self.endDirection, self.pathStatus, self.pathWeight]

        # Returns the coordinates of the current target
    def get_target(self):
        return [self.targetX, self.targetY]
    
    def target_avilable(self):
        if self.is_target:
            return True
        else:
            return False

    # Test planet
    def client_test_planet(self, planet_name):
        self.send_message(
            "explorer/007", '{"from":"client","type":"testPlanet","payload":{"planetName": "' + planet_name + '"}}')

    # Executed upon reaching the first planetary station
    def client_ready(self):
        self.send_message(
            "explorer/007", """{"from": "client","type": "ready"}""")

        sleep(2)

        self.client.subscribe(f'planet/{self.planetName}/007', qos=2)

        return self.get_planet_info()

    # Executed upon reaching the target
    def client_target_reached(self):
        self.send_message(
            "explorer/007", """{"from": "client","type": "targetReached","payload": {"message": "Target was reached"}}""")

    # Executed upon reaching the exploration target
    def client_exploration_target_reached(self):
        self.send_message(
            "explorer/007", """{"from": "client","type": "explorationCompleted","payload": {"message": "Exploration complete, final target reached"}}""")

    def client_path(self, path_info):
        """
        Send out the already completed path and recieves the correction from the mothership

        path_info = [startX, startY, startDirection, endX, endY, endDirection, pathStatus]
        """
        self.send_message(
            f"planet/{self.planetName}/007",
            '{"from": "client","type": "path","payload": {"startX": '+ str(path_info[0]) + ',"startY": '+ str(path_info[1]) + ',"startDirection": '+ str(path_info[2]) + ',"endX": '+ str(path_info[3]) + ',"endY": '+ str(path_info[4]) + ',"endDirection": '+ str(path_info[5]) + ',"pathStatus": "'+  path_info[6] + '"}}'
        )

        sleep(2)

        return self.get_path_info()

    # Executed after choosing the path
    def client_path_select(self, path_info):
        """
        Input path_info as a list with the following values

        path_info = [startX, startY, startDirrection]
        """

        direction_to_compare = path_info[2]
        self.send_message("planet/" + self.planetName + "/007", '{"from": "client","type": "pathSelect","payload": {"startX": ' +
                          str(path_info[0]) + ',"startY":' + str(path_info[1]) + ',"startDirection": ' + str(path_info[2]) + '}}')

        sleep(2)

        if (self.direction_changed):
            self.direction_changed = False
            return self.startDirection
        else:
            return direction_to_compare

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.

    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # publish(topic, payload=None, qos=0, retain=false)
        # the message should have 'from' = 'client' as it is the robot that sends out the message
        # Send the message
        self.client.publish(topic, payload=message, qos=2, retain=False)

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"

    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise
