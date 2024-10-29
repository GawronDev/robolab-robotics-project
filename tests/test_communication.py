#!/usr/bin/env python3

import unittest.mock
import paho.mqtt.client as mqtt
import uuid


from communication import Communication

"""
IMPORTANT: THOSE TESTS ARE NOT REQUIRED FOR THE EXAM AND USED ONLY FOR DEVELOPMENT
ASK YOUR TUTOR FOR SPECIFIC DETAILS ABOUT THIS!
"""


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = '007-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        print(self.communication.client_ready())

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        print(self.communication.client_path([3, 3, 0, 4, 4, 5, "free"]))


    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        print(self.communication.client_path([3.2, 3, 0, 4, 4, 5, "free"]))
    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        self.fail("implement me!")

    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        print(self.communication.client_exploration_target_reached())

if __name__ == "__main__":
    unittest.main()
