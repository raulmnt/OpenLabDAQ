# Sensor Driver Guide

## Purpose

A sensor driver translates one instrument's communication protocol into the standard OpenLabDAQ interface.

The protocol may be Arduino serial, RS-232, RS-485, Modbus, USB, or another command format. OpenLabDAQ does not need to know those details.

## Naming

The following names must match exactly:

- Python filename
- Python class name
- `NAME`
- Sensor key in `config.json`

Example:

```text
sensors/FurnaceTC.py
class FurnaceTC
NAME = "FurnaceTC"
"FurnaceTC" in config.json
```

A physical label should use the same official name when practical. Experiment-specific descriptions belong in the optional GUI nickname.

## Required Interface

```python
sensor = Sensor(port)
sensor.connect()
value = sensor.read()
sensor.disconnect()
```

### Constructor

```python
def __init__(self, port):
```

The constructor stores settings only. It should not open the instrument connection.

### `connect()`

Opens communication and verifies that the expected instrument responds.

Verification depends on the instrument:

- Arduino: request a programmed identity
- Addressed RS-485 device: verify the expected address responds
- Instrument with serial-number query: optionally verify the serial number
- Other instruments: validate a protocol-specific response

Opening a COM port alone is not sufficient verification.

Repeated calls may safely return when already connected.

### `read()`

Returns one measurement already converted to engineering units.

```python
return 523.0
```

`read()` must:

- Require an existing connection
- Never reconnect automatically
- Validate the response
- Return a numerical value
- Raise a descriptive exception on failure

### `disconnect()`

Closes communication safely and sets the connection object to `None`.

After disconnection, `read()` must fail clearly.

## Required Constants

```python
NAME = "FurnaceTC"
UNIT = "°C"
```

Drivers may define additional constants such as baud rate, Modbus address, timeout, or register address.

## Driver Responsibilities

A driver shall:

- Connect to one physical instrument
- Verify communication
- Read one measurement
- Convert the value to engineering units
- Validate framing, checksum, CRC, address, and response format when applicable
- Raise clear errors

A driver shall not:

- Save files
- Generate timestamps
- Plot data
- Read `config.json`
- Access History, Logger, or the GUI
- Automatically reopen a disconnected port
- Print routine status messages during GUI operation

## Error Handling

Return a valid numerical value or raise an exception. Do not return `None` for communication failures.

Example:

```python
if self.serial is None or not self.serial.is_open:
    raise RuntimeError(f"{self.NAME} is not connected.")
```

When opening fails, close any partially opened connection before raising the final error.

## Optional Methods

Drivers may include instrument-specific methods such as:

```python
get_status()
read_serial_number()
set_zero()
```

The DAQ backbone calls only:

```python
connect()
read()
disconnect()
```

## Acceptance Test

Every driver must pass `test_sensor.py` without changing the test logic.

The expected lifecycle is:

1. Construct the driver.
2. Connect.
3. Read a valid value.
4. Disconnect.
5. Confirm that another `read()` fails.

A driver that reconnects inside `read()` does not comply with the OpenLabDAQ interface.
