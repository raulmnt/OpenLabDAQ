"""
furnace_tc.py

Defines the FurnaceTC class used to communicate with the Arduino-based
furnace thermocouple interface.

Responsibilities
----------------
- Connect to the configured serial port.
- Verify the connected device.
- Request temperature measurements.
- Return measurements as Measurement objects.

The class does not perform logging, plotting, timestamp management,
or experiment control. Those responsibilities belong to the main DAQ
application.
"""

from datetime import datetime
import serial
import time

from measurement import Measurement


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
            Serial port assigned in config.json.
        """

        self.port = port
        self.serial = None

    def connect(self):
        """
        Connect to the furnace thermocouple.

        Returns
        -------
        bool
            True if the correct device is found.
        """

        self.serial = serial.Serial(
            self.port,
            self.BAUDRATE,
            timeout=1
        )

        # Allow the Arduino to reset.
        time.sleep(2)

        self.serial.reset_input_buffer()

        self.serial.write(b"ID?\n")

        response = self.serial.readline().decode().strip()

        return response == self.NAME

    def disconnect(self):
        """
        Close the serial connection.
        """

        if self.serial is not None:
            self.serial.close()
            self.serial = None

    def read(self):
        """
        Request one temperature measurement.

        Returns
        -------
        Measurement
            Latest furnace temperature.
        """
        # Verify that the instrument is connected.
        if self.serial is None:
            raise RuntimeError("FurnaceTC is not connected.")

        self.serial.write(b"READ?\n")

        response = self.serial.readline().decode().strip()

        return Measurement(
            name=self.NAME,
            value=float(response),
            unit=self.UNIT,
            timestamp=datetime.now()
        )

    def get_status(self):
        """
        Request the instrument status.

        Returns
        -------
        str
            Current instrument status.
        """
        if self.serial is None:
            raise RuntimeError("FurnaceTC is not connected.")
        
        self.serial.write(b"STATUS?\n")

        return self.serial.readline().decode().strip()