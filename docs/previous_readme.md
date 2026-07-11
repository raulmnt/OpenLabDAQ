# TubeFurnaceDAQ
Modular Python data acquisition software for a high-temperature tube furnace.

The project is designed around the principles of simplicity, modularity, and maintainability. Every file has a single responsibility, and every component should be easy to understand, troubleshoot, and extend.

One file = one responsibility. Prefer simple, explicit solutions over clever or highly automated ones.




| File               | Responsibility                           |
|--------------------|------------------------------------------|
| `measurement.py`   | Defines the standard measurement object. |
| `config.json`      | User-editable configuration settings.    |
| `config.py`        | Loads the configuration file.            |
| `sensors/*.py`     | Driver for each instrument.              |
| `main.py`          | Coordinates the entire DAQ system.       |
| `history.py`       | Stores recent measurements in RAM.       |
| `logger.py`        | Saves experiment data to CSV files.      |
| `gui.py`           | Displays live values and plots.          |


# Measurement Object

A `Measurement` represents one sensor reading.

Every measurement contains:

- Sensor name
- Measured value
- Engineering unit
- Timestamp

All sensor drivers return `Measurement` objects so that the rest of the software can work with a common interface.

---

# Configuration

The configuration file contains all user-editable settings.

A simple design rule is:

> **Would a user ever want to change this without modifying the source code?**

If the answer is **yes**, the setting belongs in `config.json`.

Examples include:

- Instrument COM ports
- Default logging interval
- Default data directory
- History duration

`config.py` is responsible for loading these settings into the application.
Rule #1: sensor physical label, driver file, name used in configuration and class name, must be exactly the same. main.py will make use of this convention.
Rule #2: The DAQ backbone should be experiment-independent. Any information that may change between experiments belongs in config.json, not in the Python source code.

---

# Arduino Firmware

The Arduino firmware provides a standardized interface between the physical sensor and the Python DAQ.

The firmware is responsible for:

- Identifying the instrument.
- Reading the sensor.
- Converting raw signals into engineering units.
- Responding to Python commands.
- Optionally updating a local display.

The firmware is **not** responsible for:

- Timestamping
- Data logging
- Plotting
- Experiment management
- CSV files

The Arduino continuously updates the latest measurement internally and only transmits data when requested by Python.

---

## Standard Arduino Communication Protocol

| Python Command | Arduino Response | Description                                             |
|----------------|------------------|---------------------------------------------------------|
|       `ID?`    |     `MicroBee`   | Returns the sensor identifier.                          |
|      `READ?`   |      `12.3456`   | Returns the latest measurement.                         |
|     `STATUS?`  |         `OK`     | Returns the current communication or instrument status. |

Every Arduino-based sensor in the project implements this protocol.

---

# Sensor Drivers

Each instrument has its own driver located in the `sensors/` directory.

The sensor driver is the **only** part of the software that communicates directly with the instrument.

Responsibilities include:

- Connect to the instrument.
- Disconnect from the instrument.
- Send instrument-specific commands.
- Interpret the instrument response.
- Create a timestamp.
- Return a `Measurement` object.

Each driver also contains instrument-specific information such as:

- Sensor name
- Engineering units
- Baud rate
- Communication commands
- Device address (when required)

Replacing or adding an instrument should require only adding or modifying its corresponding sensor driver.

---

# History

The history module stores recent `Measurement` objects in RAM.

It is responsible for:

- Temporary data storage
- Supplying data to the GUI
- Real-time plotting

The history module is independent of file storage.

---

# Logger

The logger is responsible for saving experiment data.

Responsibilities include:

- Creating experiment files
- Defining the CSV structure
- Writing measurements to disk

The logger receives `Measurement` objects from `main.py` and formats them for storage.

CSV formatting is handled exclusively by the logger.