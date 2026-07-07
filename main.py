"""
main.py

Test version of the Tube Furnace DAQ backbone.

This file:
- Reads config.json
- Loads enabled sensors
- Connects to them
- Reads values every acquisition period
- Builds one acquisition record
- Prints it
- Disconnects cleanly
"""

import time
from datetime import datetime
from importlib import import_module

from config import load_config


def load_sensor_class(sensor_name):
    """
    Load a sensor class using the project naming convention.

    Example:
    sensor_name = "FurnaceTC"

    Expected:
    sensors/FurnaceTC.py
    class FurnaceTC
    """

    module = import_module(f"sensors.{sensor_name}")
    sensor_class = getattr(module, sensor_name)

    return sensor_class


def create_enabled_sensors(config):
    """
    Create sensor objects for every sensor with a COM port assigned.

    Sensors with port = null are skipped.
    """

    sensors = []

    for sensor_name, port in config["ports"].items():

        if port is None:
            continue

        sensor_class = load_sensor_class(sensor_name)
        sensor = sensor_class(port)

        sensors.append(sensor)

    return sensors


def main():
    """
    Run the DAQ test loop.
    """

    config = load_config()

    period_ms = config["acquisition"]["period_ms"]
    period_seconds = period_ms / 1000

    sensors = create_enabled_sensors(config)

    print("Connecting sensors...")

    for sensor in sensors:
        sensor.connect()
        print(f"Connected: {sensor.NAME}")

    print("\nStarting acquisition...\n")

    try:
        for _ in range(10):   # test: read 10 times

            record = {}

            timestamp = datetime.now()
            record["Timestamp"] = timestamp

            for sensor in sensors:
                column_name = f"{sensor.NAME} ({sensor.UNIT})"
                record[column_name] = sensor.read()

            print(record)

            time.sleep(period_seconds)

    finally:
        print("\nDisconnecting sensors...")

        for sensor in sensors:
            sensor.disconnect()
            print(f"Disconnected: {sensor.NAME}")


if __name__ == "__main__":
    main()