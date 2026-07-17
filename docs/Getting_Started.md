# Getting Started with OpenLabDAQ

This guide covers the basic steps required to install, configure, and run OpenLabDAQ.

For information about how the source files work together, see
[Architecture](architecture.md).

For requirements when adding a new instrument, see
[Sensor Driver Guide](Sensor_Driver_Guide.md).

---

## 1. Install OpenLabDAQ

Open a terminal in the OpenLabDAQ project directory.

Create a Python virtual environment:

```powershell
py -m venv .venv
```

Install the required packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The virtual environment keeps the OpenLabDAQ dependencies separate from other
Python projects on the computer.

---

## 2. Add and Test Sensors

Each instrument used by OpenLabDAQ requires a compatible Python driver inside
the `sensors/` directory.

A driver must provide the standard OpenLabDAQ interface:

```python
connect()
read()
disconnect()
```

Before using a new driver with the complete DAQ, test it with:

```powershell
.\.venv\Scripts\python.exe test_sensor.py
```

Follow the instructions in
[Sensor Driver Guide](Sensor_Driver_Guide.md) when creating or reviewing a
driver.

---

## 3. Configure the DAQ

OpenLabDAQ reads its operating settings from `config.json`.

The configuration defines:

- System title
- Enabled sensors
- COM port for each sensor
- Optional GUI nicknames
- Acquisition period
- Data-saving directory
- History retention time

The configuration may be edited directly in `config.json` or through the
**Configuration** window in GUI mode.

The sensor name in `config.json` must match the driver filename, class name,
and `NAME` constant exactly.

Example:

```json
"FurnaceTC": {
    "enabled": true,
    "port": "COM7",
    "nickname": "Furnace Temperature"
}
```

The nickname changes only the name displayed in the GUI. CSV files keep the
official sensor name and unit.

---

## 4. Run OpenLabDAQ

OpenLabDAQ can be operated with the graphical interface or in Automatic Mode.

### GUI Mode

Run:

```text
OpenLabDAQ.bat
```

or:

```powershell
.\.venv\Scripts\python.exe GUI\gui.py
```

GUI mode provides:

- Sensor connection and acquisition controls
- Current values
- Live plots
- Selectable History ranges
- Export of displayed History
- CSV logging
- Run information and timestamped event logbooks
- Configuration and built-in Help

Detailed GUI operating instructions are available from the **Help** button
inside OpenLabDAQ.

### Automatic Mode

Run:

```powershell
.\.venv\Scripts\python.exe auto_mode.py
```

Automatic Mode is intended for unattended operation, operation without the
graphical interface, or as a backup when the GUI cannot be used.

When started, it:

1. Loads `config.json`.
2. Initializes and connects all enabled sensors.
3. Starts acquisition immediately.
4. Starts saving measurements automatically.
5. Continues until stopped by the user.
6. Disconnects the sensors safely before closing.

Automatic Mode uses the same DAQ backbone and sensor drivers as GUI mode, but
does not open the graphical interface or provide interactive logbook events.

---

## 5. Output Files

Files are saved in the directory selected in `config.json` or the GUI
Configuration window.

### GUI Logging

Starting logging in GUI mode creates:

```text
2026-07-17_12-58-00.csv
2026-07-17_12-58-00_logbook.txt
```

The CSV file contains synchronized sensor measurements.

The logbook contains:

- Experiment
- Sample
- Gas
- Operator
- General notes
- Timestamped events
- Start and end times

### Automatic Mode

Automatic Mode saves measurements directly to a CSV file.

### History Export

The **Export Data** button saves all measurements contained in the currently
selected History range.

History export is separate from normal logging.

---

## 6. History and Permanent Data

OpenLabDAQ keeps recent measurements in computer memory for plotting and
display.

History is temporary:

- It is not automatically permanent.
- It resets when a new DAQ session begins.
- It is lost when the program closes.

Use normal logging or **Export Data** when measurements must be preserved.

---

## 7. Stopping OpenLabDAQ

In GUI mode, stop acquisition using the **RUNNING** button before closing the
program.

In Automatic Mode, stop the program with:

```text
Ctrl+C
```

OpenLabDAQ will attempt to close the CSV file and disconnect all sensors
safely.

---

## Basic Troubleshooting

### A sensor does not connect

Check:

- Instrument power
- USB or serial cable
- Selected COM port
- Instrument communication settings
- Whether another program is already using the port

### The wrong instrument is connected

A compliant sensor driver should verify the expected instrument during
`connect()` and raise a clear error when verification fails.

### No CSV file is created

Confirm that:

- The saving directory exists and is writable
- Acquisition is running
- Logging has started
- At least one acquisition record has been produced

### The GUI cannot be started

Use Automatic Mode to confirm that configuration, sensor drivers, acquisition,
and CSV logging still operate without the graphical interface.

### A new driver works alone but not in OpenLabDAQ

Confirm that:

- The driver passes `test_sensor.py`
- The filename, class name, `NAME`, and `config.json` entry match
- `read()` returns a numerical value
- Communication failures raise exceptions instead of returning `None`
