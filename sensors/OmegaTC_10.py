"""
OmegaTC_10.py

OpenLabDAQ driver for an Omega CN7500 temperature controller.

Communication:
- Modbus RTU
- 9600 baud
- 8 data bits
- Even parity
- 1 stop bit
- Process-value register: 0x1000

Driver behavior:
- connect() opens the port and verifies that the expected Modbus
  address responds correctly.
- read() returns one temperature value in degrees Celsius.
- disconnect() closes the serial port.
- read() never reconnects automatically.
"""

import time

import serial


class OmegaTC_10:
    NAME = "OmegaTC_10"
    UNIT = "°C"

    # Serial communication settings
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN
    STOPBITS = serial.STOPBITS_ONE
    TIMEOUT = 1.0

    # This acts as the configured identity of this controller.
    SLAVE_ADDRESS = 10

    # Omega CN7500 process-value register
    PROCESS_VALUE_REGISTER = 0x1000

    # Modbus function code: Read Holding Registers
    READ_REGISTER_FUNCTION = 0x03

    # Special values returned by the process-value register
    PROCESS_VALUE_ERRORS = {
        0x8002: "Temperature is not available yet.",
        0x8003: "The temperature sensor is disconnected.",
        0x8004: "The controller reports an input-signal error.",
        0x8006: "The controller reports an ADC failure.",
    }

    def __init__(self, port):
        self.port = port
        self.serial = None

    def connect(self):
        """
        Open the serial port and verify that the expected controller responds.

        Verification confirms:
        - The COM port opens.
        - The expected Modbus address responds.
        - The response function and byte count are correct.
        - The response CRC is valid.

        Raises
        ------
        RuntimeError
            If the port cannot be opened or the expected controller
            does not provide a valid response.
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

            # Allow the USB-RS485 adapter to finish opening.
            time.sleep(0.2)

            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Read the PV register once to verify communication.
            # The returned word may contain a sensor error, but a valid
            # Modbus response still confirms the controller address.
            self._read_register_word(self.PROCESS_VALUE_REGISTER)

        except (serial.SerialException, serial.SerialTimeoutException) as error:
            self.disconnect()

            raise RuntimeError(
                f"{self.NAME} could not open {self.port}: {error}"
            ) from error

        except RuntimeError as error:
            self.disconnect()

            raise RuntimeError(
                f"{self.NAME} could not verify a controller at "
                f"Modbus address {self.SLAVE_ADDRESS} on {self.port}. "
                f"{error}"
            ) from error

    def disconnect(self):
        """
        Close the serial connection.
        """
        if self.serial is not None:
            try:
                if self.serial.is_open:
                    self.serial.close()
            finally:
                self.serial = None

    def read(self):
        """
        Read and return the current process temperature.

        Returns
        -------
        float
            Temperature in degrees Celsius.

        Raises
        ------
        RuntimeError
            If the driver is disconnected, communication fails,
            the response is invalid, or the controller reports
            a temperature-input error.
        """
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError(f"{self.NAME} is not connected.")

        raw_word = self._read_register_word(
            self.PROCESS_VALUE_REGISTER
        )

        if raw_word in self.PROCESS_VALUE_ERRORS:
            raise RuntimeError(
                f"{self.NAME}: "
                f"{self.PROCESS_VALUE_ERRORS[raw_word]}"
            )

        # Convert the normal 16-bit value to a signed integer.
        signed_value = int.from_bytes(
            raw_word.to_bytes(2, byteorder="big"),
            byteorder="big",
            signed=True,
        )

        # The controller reports the PV in units of 0.1 degree.
        temperature = signed_value / 10.0

        return temperature

    def _read_register_word(self, register_address):
        """
        Read one 16-bit Modbus register.

        Parameters
        ----------
        register_address : int
            Modbus register address.

        Returns
        -------
        int
            Register value as an unsigned 16-bit integer.
        """
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError(f"{self.NAME} is not connected.")

        request_without_crc = bytes(
            [
                self.SLAVE_ADDRESS,
                self.READ_REGISTER_FUNCTION,
                (register_address >> 8) & 0xFF,
                register_address & 0xFF,
                0x00,
                0x01,
            ]
        )

        request = request_without_crc + self._calculate_crc(
            request_without_crc
        )

        try:
            self.serial.reset_input_buffer()
            self.serial.write(request)
            self.serial.flush()

            # A normal response begins with:
            # address, function, byte count
            header = self.serial.read(3)

        except (serial.SerialException, serial.SerialTimeoutException) as error:
            raise RuntimeError(
                f"Serial communication failed on {self.port}: {error}"
            ) from error

        if len(header) == 0:
            raise RuntimeError(
                f"No response from Modbus address "
                f"{self.SLAVE_ADDRESS}."
            )

        if len(header) != 3:
            raise RuntimeError(
                f"Incomplete Modbus response header: {header!r}"
            )

        response_address = header[0]
        response_function = header[1]
        third_byte = header[2]

        if response_address != self.SLAVE_ADDRESS:
            raise RuntimeError(
                f"Expected response from Modbus address "
                f"{self.SLAVE_ADDRESS}, but received address "
                f"{response_address}."
            )

        # Modbus exception responses use function code + 0x80.
        if response_function == (
            self.READ_REGISTER_FUNCTION | 0x80
        ):
            exception_tail = self.serial.read(2)
            exception_frame = header + exception_tail

            if len(exception_frame) != 5:
                raise RuntimeError(
                    "Incomplete Modbus exception response."
                )

            self._validate_crc(exception_frame)

            raise RuntimeError(
                f"Controller returned Modbus exception code "
                f"0x{third_byte:02X}."
            )

        if response_function != self.READ_REGISTER_FUNCTION:
            raise RuntimeError(
                f"Expected Modbus function "
                f"0x{self.READ_REGISTER_FUNCTION:02X}, "
                f"but received 0x{response_function:02X}."
            )

        byte_count = third_byte

        if byte_count != 2:
            raise RuntimeError(
                f"Expected 2 data bytes, but the controller "
                f"reported {byte_count}."
            )

        # Two data bytes followed by two CRC bytes
        response_tail = self.serial.read(byte_count + 2)
        response = header + response_tail

        expected_length = 3 + byte_count + 2

        if len(response) != expected_length:
            raise RuntimeError(
                f"Incomplete Modbus response. Expected "
                f"{expected_length} bytes, received "
                f"{len(response)}."
            )

        self._validate_crc(response)

        data_bytes = response[3:5]

        return int.from_bytes(
            data_bytes,
            byteorder="big",
            signed=False,
        )

    def _validate_crc(self, response):
        """
        Validate the CRC of a complete Modbus RTU response.
        """
        received_crc = response[-2:]
        expected_crc = self._calculate_crc(response[:-2])

        if received_crc != expected_crc:
            raise RuntimeError(
                "Modbus CRC mismatch. The response may be corrupted."
            )

    @staticmethod
    def _calculate_crc(data):
        """
        Calculate the Modbus RTU CRC-16 checksum.

        Parameters
        ----------
        data : bytes
            Modbus frame without its CRC.

        Returns
        -------
        bytes
            Two CRC bytes in Modbus little-endian order.
        """
        crc = 0xFFFF

        for byte in data:
            crc ^= byte

            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        return crc.to_bytes(2, byteorder="little")