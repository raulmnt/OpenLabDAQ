"""
this is just a copy of furnaceTC code to be used with an arduino as a test
"""

import serial
import time


class LightSensor:
    """
    Driver for the Arduino-based light sensor.
    """

    NAME = "LightSensor"
    UNIT = "lux"
    BAUDRATE = 9600

    def __init__(self, port):
        """
        Create a LightSensor object.

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
            If the connected device is not a LightSensor.
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
        Read the current light intensity.

        Returns
        -------
        float
            Current light intensity in lux.

        Raises
        ------
        RuntimeError
            If the sensor is not connected or returns invalid data.
        """

        if self.serial is None:
            raise RuntimeError(f"{self.NAME} is not connected.")

        # Remove any old unread data before sending a new command.
        self.serial.reset_input_buffer()

        self.serial.write(b"READ?\n")
        self.serial.flush()

        response = self.serial.readline().decode().strip()

        if response == "":
            raise RuntimeError(
                f"{self.NAME} returned no response."
            )

        if response == "ERROR":
            raise RuntimeError(
                f"{self.NAME} reported a sensor error."
            )

        try:
            return float(response)

        except ValueError as error:
            raise RuntimeError(
                f"{self.NAME} returned an invalid value: {response!r}"
            ) from error


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