"""
FurnaceTC.py

Driver for the Arduino-based furnace thermocouple.

Purpose
-------
The FurnaceTC driver translates the Arduino serial communication
protocol into the standard interface used by the Tube Furnace DAQ.

Responsibilities
----------------
- Connect to the configured serial port.
- Verify the connected instrument.
- Read the current temperature.
- Disconnect from the instrument.

The driver does not perform logging, plotting, timestamp generation,
or experiment control.
"""

import serial
import time


class FurnaceTC:
    """
    Driver for the Arduino-based furnace thermocouple.
    """

    NAME = "FurnaceTC"
    UNIT = "C"
    BAUDRATE = 9600

    def __init__(self, port):
        """
        Create a FurnaceTC object.

        Parameters
        ----------
        port : str
            Communication port assigned by the DAQ.
        """

        self.port = port
        self.serial = None

    def connect(self):
        """
        Connect to the instrument and verify its identity.

        Raises
        ------
        RuntimeError
            If the connected device is not a FurnaceTC.
        """

        self.serial = serial.Serial(
            self.port,
            self.BAUDRATE,
            timeout=1
        )

        # Allow the Arduino to reset after opening the serial port.
        time.sleep(2)

        self.serial.reset_input_buffer()

        self.serial.write(b"ID?\n")

        response = self.serial.readline().decode().strip()

        if response != self.NAME:
            self.disconnect()
            raise RuntimeError(
                f"Expected {self.NAME}, but received '{response}'."
            )

    def disconnect(self):
        """
        Close the serial connection.
        """

        if self.serial is not None:
            self.serial.close()
            self.serial = None

    def read(self):
        """
        Read the current furnace temperature.

        Returns
        -------
        float
            Current furnace temperature in degrees Celsius.

        Raises
        ------
        RuntimeError
            If the sensor is not connected.
        """

        if self.serial is None:
            raise RuntimeError(f"{self.NAME} is not connected.")

        self.serial.write(b"READ?\n")

        response = self.serial.readline().decode().strip()

        return float(response)

    def get_status(self):
        """
        Return the current instrument status.

        This is an optional driver-specific method and is not used by
        the DAQ backbone.
        """

        if self.serial is None:
            raise RuntimeError(f"{self.NAME} is not connected.")

        self.serial.write(b"STATUS?\n")

        return self.serial.readline().decode().strip()