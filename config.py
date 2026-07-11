"""
config.py

Loads and saves the OpenLabDAQ configuration.

The configuration file is the single source of truth for:
- Enabled sensors
- Sensor COM ports
- Acquisition period
- Logging directory
- History retention

The configuration path is based on this file's location, so the
program works correctly regardless of the current working directory.
"""

import json
from pathlib import Path


# config.json is stored in the project root beside config.py.
CONFIG_FILE = Path(__file__).resolve().parent / "config.json"


def load_config():
    """
    Load and return the OpenLabDAQ configuration.

    Returns
    -------
    dict
        Complete configuration dictionary.
    """

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config):
    """
    Save the complete OpenLabDAQ configuration.

    Parameters
    ----------
    config : dict
        Complete configuration dictionary.
    """

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=4,
        )

        # Add a final newline to keep the JSON file readable.
        file.write("\n")