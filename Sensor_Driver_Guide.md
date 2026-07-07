# Sensor Driver Guide

## Purpose

A sensor driver acts as a translator between a physical instrument and the Tube Furnace DAQ.

Each instrument may use its own communication protocol (Arduino, RS-232, RS-485, USB, VISA, Modbus, etc.). The purpose of the sensor driver is to translate that protocol into the standard commands understood by the DAQ.

The internal communication with the instrument is completely up to the developer. However, every sensor driver must be implemented as a Python class that provides the standard DAQ interface described in this document.
---

# Naming Convention

Each sensor has one canonical name.

The following must match exactly:

- Physical label on the instrument
- Python filename
- Python class name
- Sensor identifier (`NAME`)
- Configuration file entry

Example

Sensor name: `FurnaceTC`

```
FurnaceTC.py
class FurnaceTC
NAME = "FurnaceTC"
"FurnaceTC" in config.json
```

---

# Responsibilities

A sensor driver SHALL

- Connect to one physical instrument.
- Disconnect from the instrument.
- Return the current measurement.
- Identify the sensor.
- Report the engineering unit.

A sensor driver SHALL NOT

- Save files.
- Plot data.
- Generate timestamps.
- Communicate with other sensors.
- Read the configuration file.
- Know about experiments.
- Know about History.
- Know about Logger.
- Know about the GUI.

Its only responsibility is to communicate with one physical instrument and translate its native protocol into the standard DAQ interface.

---

# Standard DAQ Interface

Every sensor driver must implement the following interface exactly.

The DAQ backbone communicates with every sensor driver using only these commands.

No additional commands are required.

---

## Constructor

```python
sensor = Sensor(port)
```

### Input

```
Communication port
```

Example

```
COM8
```

### Purpose

Store the communication settings.

The constructor should not establish communication with the instrument.

---

## connect()

### Purpose

Establish communication with the instrument.

### Input

None.

### Output

The sensor is connected and ready to acquire data.

---

## disconnect()

### Purpose

Close communication with the instrument.

### Input

None.

### Output

Communication is closed.

---

## read()

### Purpose

Return the current measurement.

### Input

None.

### Output

A single floating-point value.

Example

```python
1000.25
```

The value shall already be converted into engineering units.

The driver shall not print, plot, timestamp, or save the measurement.

---

## Required Constants

Every sensor driver must define the following constants.

### NAME

Unique sensor identifier.

Example

```python
NAME = "FurnaceTC"
```

---

### UNIT

Engineering unit returned by `read()`.

Example

```python
UNIT = "°C"
```

---

# Acceptance Test

Every sensor driver shall pass the standard `test_sensor.py` program without modifying the test logic. Read instructions on the test_sensor.py file.

If additional modifications are required, the sensor driver does not comply with the Tube Furnace DAQ communication standard.