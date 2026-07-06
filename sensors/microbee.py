"""
microbee.py

Defines the MicroBee class used to communicate with the Arduino-based
MicroBee pressure gauge.

The class is responsible for:

- Automatically detecting the correct serial port.
- Establishing and closing the serial connection.
- Communicating with the Arduino using the standard DAQ protocol.
- Requesting pressure measurements from the sensor.
- Returning each measurement as a Measurement object with a Python timestamp.

"""

from datetime import datetime
import time
from urllib import response

import serial
from serial.tools import list_ports

from measurement import Measurement


class MicroBee:

    NAME = "MicroBee"
    UNIT = "Torr"
    BAUDRATE = 9600

    def __init__(self):
        """Create a disconnected MicroBee object."""
        self.serial = None

    def connect(self):
        """
        Search all COM ports until a MicroBee is found.

        Returns
        -------
        bool
            True if connected successfully.
        """

        for port in list_ports.comports():

            try:

                ser = serial.Serial(
                    port.device,
                    self.BAUDRATE,
                    timeout=1
                )

                # Allow Arduino to reboot.
                time.sleep(2)

                # Stop streaming first.
                ser.write(b"STREAM OFF\n")
                time.sleep(0.2)

                # Clear any measurements already in the buffer.
                ser.reset_input_buffer()

                # Now ask for the device ID.
                ser.write(b"ID?\n")

                response = ser.readline().decode(errors="ignore").strip()

                if response == self.NAME:

                    # Stop continuous streaming.
                    ser.write(b"STREAM OFF\n")

                    self.serial = ser
                    return True

                ser.close()

            except Exception:
                pass

        return False

    def disconnect(self):
        """Disconnect from the sensor."""

        if self.serial is not None:

            # Resume streaming for Arduino Serial Monitor.
            self.serial.write(b"STREAM ON\n")

            self.serial.close()
            self.serial = None

    def read(self):
        """
        Request one measurement from the Arduino.
        """

        if self.serial is None:
            raise RuntimeError("MicroBee is not connected.")

        self.serial.reset_input_buffer()

        self.serial.write(b"READ?\n")

        value = float(
            self.serial.readline().decode().strip()
        )

        return Measurement(
            name=self.NAME,
            value=value,
            unit=self.UNIT,
            timestamp=datetime.now()
        )