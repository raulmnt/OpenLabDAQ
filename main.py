"""
main.py

Tube Furnace DAQ Backbone

Purpose
-------
Coordinates the complete data acquisition process.

Responsibilities
----------------
- Load the system configuration.
- Create the enabled sensor drivers.
- Connect to all sensors.
- Acquire one record every acquisition period.
- Send every acquisition record to History.
- Display the acquisition record.
- Disconnect all sensors before exiting.

Future versions will add:

- Logger integration.
- GUI integration.
- User commands.
"""

from datetime import datetime
from importlib import import_module
import time

from config import load_config
from history import History
from logger import Logger


# ---------------------------------------------------------------------
# Load one sensor class.
# ---------------------------------------------------------------------

def load_sensor_class(sensor_name):
    """
    Load the sensor class that matches the sensor name.

    Example
    -------
    Sensor name:

        FurnaceTC

    Expected file:

        sensors/FurnaceTC.py

    Expected class:

        class FurnaceTC
    """

    module = import_module(f"sensors.{sensor_name}")

    return getattr(module, sensor_name)


# ---------------------------------------------------------------------
# Create all enabled sensors.
# ---------------------------------------------------------------------

def create_enabled_sensors(config):
    """
    Create one sensor object for every enabled sensor.

    Sensors with port = null are ignored.
    """

    sensors = []

    for sensor_name, port in config["ports"].items():

        if port is None:
            continue

        sensor_class = load_sensor_class(sensor_name)

        sensor = sensor_class(port)

        sensors.append(sensor)

    return sensors


# ---------------------------------------------------------------------
# Connect all sensors.
# ---------------------------------------------------------------------

def connect_sensors(sensors):
    """
    Connect every enabled sensor.
    """

    print("\nConnecting sensors...")

    for sensor in sensors:

        sensor.connect()

        print(f"Connected: {sensor.NAME}")


# ---------------------------------------------------------------------
# Disconnect all sensors.
# ---------------------------------------------------------------------

def disconnect_sensors(sensors):
    """
    Disconnect every enabled sensor.
    """

    print("\nDisconnecting sensors...")

    for sensor in sensors:

        sensor.disconnect()

        print(f"Disconnected: {sensor.NAME}")


# ---------------------------------------------------------------------
# Main program.
# ---------------------------------------------------------------------

def main():

    # --------------------------------------------------------------
    # Load configuration.
    # --------------------------------------------------------------

    config = load_config()

    period = config["acquisition"]["period_ms"] / 1000

    # --------------------------------------------------------------
    # Create DAQ modules.
    # --------------------------------------------------------------

    history = History()

    logger = Logger(config["logging"]["default_directory"])

    sensors = create_enabled_sensors(config)

    # --------------------------------------------------------------
    # Connect sensors.
    # --------------------------------------------------------------

    connect_sensors(sensors)

    print("\nStarting acquisition...\n")

    try:

        while True:

            # ------------------------------------------------------
            # Create one acquisition record.
            # ------------------------------------------------------

            timestamp = datetime.now()

            record = {
                "Timestamp": timestamp
            }

            for sensor in sensors:

                column = f"{sensor.NAME} ({sensor.UNIT})"

                record[column] = sensor.read()

            # ------------------------------------------------------
            # Send record to History.
            # ------------------------------------------------------

            history.add(record)

            # ------------------------------------------------------
            # Display acquisition record.
            # ------------------------------------------------------

            print(record)

            time.sleep(period)

    except KeyboardInterrupt:

        print("\nAcquisition stopped by user.")

    finally:

        disconnect_sensors(sensors)


# ---------------------------------------------------------------------
# Program entry point.
# ---------------------------------------------------------------------

if __name__ == "__main__":

    main()