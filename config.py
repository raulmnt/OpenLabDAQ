"""
config.py

Loads the user configuration from config.json.

This module provides a single function for reading the configuration
file so that the rest of the DAQ software can access user-defined
settings such as COM ports, logging options, and history settings.

The configuration file is intended to contain all settings that a user
may wish to modify without editing the Python source code.
"""

# Import the JSON library to read the configuration file.
import json


def load_config():
    """
    Load the DAQ configuration file.

    Returns
    -------
    dict
        Dictionary containing all configuration settings.
    """

    # Open the configuration file.
    with open("config.json", "r") as file:

        # Read and return the JSON data.
        return json.load(file)