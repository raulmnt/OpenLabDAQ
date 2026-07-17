"""
MassFlow.py

OpenLabDAQ driver for a Sierra Instruments SmartTrak Series 100
mass-flow meter or controller.

Communication
-------------
- RS-232 ASCII protocol
- 9600 baud, 8 data bits, no parity, 1 stop bit
- Flow command: ?Flow + SmartTrak CRC + <CR>
- Expected response: Flow + value + SmartTrak CRC + <CR>

Driver behavior
---------------
- connect() opens the serial port and verifies that a compatible SmartTrak
  responds with a valid flow frame and CRC.
- read() returns one mass-flow value in scc/m.
- disconnect() closes the serial port.
- read() never opens or reconnects the serial port automatically.

The SmartTrak CRC is not Modbus CRC. It uses the manufacturer-specified
CRC-16 algorithm with polynomial 0x1021 and transmits the high byte first.
"""

import re
import time

import serial


class MassFlow:
    NAME = "MassFlow"
    UNIT = "scc/m"

    # Serial communication settings
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_NONE
    STOPBITS = serial.STOPBITS_ONE
    TIMEOUT = 1.0

    # Optional physical-instrument verification.
    #
    # Leave as None to accept any compatible SmartTrak.
    # To require one specific SmartTrak, enter its serial number exactly
    # as returned by the ?Srnm command. This query is documented for
    # SmartTrak firmware version 2.xx.
    EXPECTED_SERIAL_NUMBER = None

    _FLOW_PATTERN = re.compile(
        r"^Flow([+-]?(?:\d+(?:\.\d*)?|\.\d+)"
        r"(?:[Ee][+-]?\d+)?)$"
    )

    def __init__(self, port):
        self.port = port
        self.serial = None
        self.instrument_serial_number = None

    def connect(self):
        """
        Open the serial port and verify SmartTrak communication.

        Verification confirms:
        - the COM port opens,
        - a compatible SmartTrak returns a valid Flow response, and
        - the response CRC is correct.

        When EXPECTED_SERIAL_NUMBER is configured, connect() additionally
        verifies the physical SmartTrak serial number.

        Raises
        ------
        RuntimeError
            If the port cannot be opened or verification fails.
        """
        if self.serial is not None and self.serial.is_open:
            return

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

            # A valid Flow response verifies the SmartTrak protocol.
            self.read()

            # Optional verification of one specific physical instrument.
            if self.EXPECTED_SERIAL_NUMBER is not None:
                self.instrument_serial_number = (
                    self._read_serial_number()
                )

                expected = str(
                    self.EXPECTED_SERIAL_NUMBER
                ).strip()

                if self.instrument_serial_number != expected:
                    raise RuntimeError(
                        f"Expected SmartTrak serial number "
                        f"{expected!r}, but received "
                        f"{self.instrument_serial_number!r}."
                    )

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
                f"{self.NAME} could not verify a SmartTrak on "
                f"{self.port}. {error}"
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
                self.instrument_serial_number = None

    def read(self):
        """
        Read and return the current mass-flow value.

        Returns
        -------
        float
            Current flow in the instrument's configured engineering units.

        Raises
        ------
        RuntimeError
            If disconnected, communication fails, the response is invalid,
            or the response CRC does not match.
        """
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError(f"{self.NAME} is not connected.")

        response_payload = self._exchange(b"?Flow")

        try:
            response_text = response_payload.decode("ascii")

        except UnicodeDecodeError as error:
            raise RuntimeError(
                f"SmartTrak returned non-ASCII flow data: "
                f"{response_payload!r}"
            ) from error

        if response_text.startswith("Err"):
            raise RuntimeError(
                f"SmartTrak reported an error: {response_text}"
            )

        match = self._FLOW_PATTERN.fullmatch(response_text)

        if match is None:
            raise RuntimeError(
                f"Unexpected SmartTrak flow response: "
                f"{response_text!r}"
            )

        try:
            return float(match.group(1))

        except ValueError as error:
            raise RuntimeError(
                f"Could not convert SmartTrak flow to a number: "
                f"{match.group(1)!r}"
            ) from error

    def _read_serial_number(self):
        """
        Read the SmartTrak serial number using the version-2.xx command.
        """
        response_payload = self._exchange(b"?Srnm")

        try:
            response_text = response_payload.decode("ascii")

        except UnicodeDecodeError as error:
            raise RuntimeError(
                f"SmartTrak returned a non-ASCII serial number: "
                f"{response_payload!r}"
            ) from error

        if response_text.startswith("Err"):
            raise RuntimeError(
                f"SmartTrak rejected the serial-number query: "
                f"{response_text}"
            )

        if not response_text.startswith("Srnm"):
            raise RuntimeError(
                f"Unexpected SmartTrak serial-number response: "
                f"{response_text!r}"
            )

        serial_number = response_text[4:].strip()

        if not serial_number:
            raise RuntimeError(
                "SmartTrak returned an empty serial number."
            )

        return serial_number

    def _exchange(self, command_payload):
        """
        Send one SmartTrak command and return its validated response payload.

        The returned payload excludes the two CRC bytes and carriage return.
        """
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError(f"{self.NAME} is not connected.")

        command = (
            command_payload
            + self.calculate_crc(command_payload)
            + b"\r"
        )

        try:
            self.serial.reset_input_buffer()
            self.serial.write(command)
            self.serial.flush()

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
                "No response received from the SmartTrak."
            )

        if not raw_response.endswith(b"\r"):
            raise RuntimeError(
                f"Incomplete SmartTrak response: {raw_response!r}"
            )

        # Remove the carriage return. The remaining frame must contain
        # at least one payload byte and two CRC bytes.
        response_frame = raw_response[:-1]

        if len(response_frame) < 3:
            raise RuntimeError(
                f"SmartTrak response is too short: {raw_response!r}"
            )

        response_payload = response_frame[:-2]
        received_crc = response_frame[-2:]
        expected_crc = self.calculate_crc(response_payload)

        if received_crc != expected_crc:
            raise RuntimeError(
                "SmartTrak response CRC mismatch. "
                f"Expected {expected_crc.hex().upper()}, "
                f"received {received_crc.hex().upper()}."
            )

        return response_payload

    @staticmethod
    def calculate_crc(data):
        """
        Calculate the manufacturer-specified SmartTrak CRC-16.

        This is a CRC-16/CCITT-style calculation using polynomial 0x1021,
        initialized to 0xFFFF. The high byte is transmitted first.

        SmartTrak does not permit 0x00 or 0x0D in either CRC byte, so any
        CRC byte with one of those values is incremented by one.
        """
        crc = 0xFFFF

        for byte in data:
            crc ^= byte << 8

            for _ in range(8):
                if crc & 0x8000:
                    crc = (
                        (crc << 1) ^ 0x1021
                    ) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF

        high_byte = (crc >> 8) & 0xFF
        low_byte = crc & 0xFF

        if high_byte in (0x00, 0x0D):
            high_byte += 1

        if low_byte in (0x00, 0x0D):
            low_byte += 1

        return bytes(
            [
                high_byte,
                low_byte,
            ]
        )
