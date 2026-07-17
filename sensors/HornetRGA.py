"""
HornetRGA.py

OpenLabDAQ driver for an InstruTech Hornet vacuum gauge.

Communication
-------------
- RS-485 ASCII protocol
- 19200 baud, 8 data bits, no parity, 1 stop bit
- Pressure command: #xxRD<CR>
- Expected response: *xx pressure<CR>

Driver behavior
---------------
- connect() opens the serial port and verifies that the Hornet configured
  with the expected RS-485 address responds correctly.
- read() returns one pressure value in Torr.
- disconnect() closes the serial port.
- read() never opens or reconnects the serial port automatically.

The RS-485 address is stored in the Hornet itself. The factory-default
address is 1, represented by "01" in the ASCII protocol. A different
address can be assigned through the Hornet communication settings.
"""

import re
import time

import serial


class HornetRGA:
    NAME = "HornetRGA"
    UNIT = "Torr"

    # Serial communication settings
    BAUDRATE = 19200
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_NONE
    STOPBITS = serial.STOPBITS_ONE
    TIMEOUT = 1.0

    # Two-character hexadecimal RS-485 address stored in the Hornet.
    ADDRESS = "01"

    # Accept ordinary decimal or scientific-notation pressure values.
    _NUMBER_PATTERN = re.compile(
        r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$"
    )

    def __init__(self, port):
        self.port = port
        self.serial = None

    def connect(self):
        """
        Open the serial port and verify the expected Hornet address.

        A successful pressure response confirms that:
        - the COM port is usable,
        - a compatible Hornet-protocol device is responding, and
        - the responding device has the expected RS-485 address.

        Raises
        ------
        RuntimeError
            If the port cannot be opened or the expected device does not
            return a valid response.
        """
        if self.serial is not None and self.serial.is_open:
            return

        self._validate_address()

        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.BAUDRATE,
                bytesize=self.BYTESIZE,
                parity=self.PARITY,
                stopbits=self.STOPBITS,
                timeout=self.TIMEOUT,
                write_timeout=self.TIMEOUT,
            )

            # Allow the USB serial adapter to finish opening.
            time.sleep(0.1)

            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Verify the instrument and address by reading pressure once.
            self.read()

        except (
            serial.SerialException,
            serial.SerialTimeoutException,
        ) as error:
            self.disconnect()
            raise RuntimeError(
                f"{self.NAME} could not open {self.port}: {error}"
            ) from error

        except RuntimeError as error:
            self.disconnect()
            raise RuntimeError(
                f"{self.NAME} could not verify a Hornet at address "
                f"{self.ADDRESS} on {self.port}. {error}"
            ) from error

    def disconnect(self):
        """
        Close the serial connection safely.
        """
        if self.serial is not None:
            try:
                if self.serial.is_open:
                    self.serial.close()
            finally:
                self.serial = None

    def read(self):
        """
        Read and return the current pressure.

        Returns
        -------
        float
            Pressure in Torr.

        Raises
        ------
        RuntimeError
            If disconnected, communication fails, or the response is invalid.
        """
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError(f"{self.NAME} is not connected.")

        command = f"#{self.ADDRESS}RD\r".encode("ascii")

        try:
            self.serial.reset_input_buffer()
            self.serial.write(command)
            self.serial.flush()

            # Hornet responses are terminated by a carriage return.
            raw_response = self.serial.read_until(b"\r")

        except (
            serial.SerialException,
            serial.SerialTimeoutException,
        ) as error:
            raise RuntimeError(
                f"{self.NAME} serial communication failed on "
                f"{self.port}: {error}"
            ) from error

        if not raw_response:
            raise RuntimeError(
                f"No response from Hornet address {self.ADDRESS}."
            )

        if not raw_response.endswith(b"\r"):
            raise RuntimeError(
                f"Incomplete Hornet response: {raw_response!r}"
            )

        try:
            response = raw_response[:-1].decode("ascii").strip()

        except UnicodeDecodeError as error:
            raise RuntimeError(
                f"Hornet returned non-ASCII data: {raw_response!r}"
            ) from error

        expected_prefix = f"*{self.ADDRESS}"

        if response.startswith("?"):
            raise RuntimeError(
                f"Hornet reported a communication error: {response}"
            )

        if not response.startswith(expected_prefix):
            raise RuntimeError(
                f"Expected a response from Hornet address "
                f"{self.ADDRESS}, but received: {response!r}"
            )

        # Remove the response address and any separator spaces/underscores.
        pressure_text = response[len(expected_prefix):].lstrip(" _")

        if not self._NUMBER_PATTERN.fullmatch(pressure_text):
            raise RuntimeError(
                f"Hornet returned an invalid pressure value: "
                f"{response!r}"
            )

        try:
            return float(pressure_text)

        except ValueError as error:
            raise RuntimeError(
                f"Could not convert Hornet pressure to a number: "
                f"{pressure_text!r}"
            ) from error

    @classmethod
    def _validate_address(cls):
        """
        Confirm that ADDRESS is exactly one hexadecimal byte.
        """
        if not re.fullmatch(r"[0-9A-Fa-f]{2}", cls.ADDRESS):
            raise RuntimeError(
                f"{cls.NAME} ADDRESS must contain exactly two "
                f"hexadecimal characters, not {cls.ADDRESS!r}."
            )

        cls.ADDRESS = cls.ADDRESS.upper()
