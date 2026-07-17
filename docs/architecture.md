# OpenLabDAQ Architecture

## Purpose

OpenLabDAQ acquires synchronized measurements from multiple laboratory instruments while keeping instrument communication, acquisition, storage, and display separate.

The architecture is intentionally simple:

- Sensor drivers communicate with instruments.
- `daq.py` coordinates acquisition.
- `history.py` keeps recent records in memory.
- `logger.py` writes permanent CSV files.
- The GUI reads History and controls the DAQ.
- `auto_mode.py` runs the same DAQ backbone without the GUI.

## Data Flow

```text
config.json
    │
    ▼
config.py
    │
    ▼
daq.py
    ├── sensors/<Driver>.py ──► physical instruments
    │
    ├──► history.py ──► GUI values and plots
    │                 └──► Export displayed data
    │
    └──► logger.py ──► CSV file, when logging is enabled

GUI/gui.py
    ├── controls daq.py
    ├── reads history.py
    └── controls logbook.py ──► matching _logbook.txt file

auto_mode.py
    └── runs daq.py without the GUI
```

## Acquisition Record

Each acquisition cycle produces one dictionary with a single timestamp and one value from every enabled sensor.

```python
{
    "Timestamp": datetime_object,
    "FurnaceTC (°C)": 523,
    "HornetRGA (Torr)": 4.9e-8,
    "MassFlow (scc/m)": 10.0,
}
```

This record is the standard data format shared by the DAQ, History, Logger, and GUI.

## Module Responsibilities

### `config.json`

Stores user-selectable settings:

- System title
- Enabled sensors
- COM ports
- Optional GUI nicknames
- Acquisition period
- Logging directory
- History retention

The sensor key is the official driver name. A nickname changes only what is displayed in the GUI; History and CSV headers keep the official name.

### `config.py`

Loads and saves `config.json`.

### `sensors/`

Each file contains one sensor driver. A driver translates an instrument protocol into the standard methods:

```python
connect()
read()
disconnect()
```

Drivers do not timestamp, log, plot, or read the project configuration.

### `daq.py`

The DAQ backbone is the only project module that communicates with sensor drivers.

It:

- Loads enabled sensors from configuration
- Connects and disconnects sensors
- Requests one value from each sensor
- Creates one timestamp per acquisition cycle
- Builds the acquisition record
- Sends records to History
- Sends records to Logger when logging is enabled

### `history.py`

Keeps recent acquisition records in RAM.

History supports:

- Current sensor values
- Live plots
- Time-window selection
- Export of displayed data

History is temporary. It resets when a new DAQ session starts or the program closes.

### `logger.py`

Writes acquisition records to CSV files.

Logger creates the file, writes the header, appends records, and exposes the active file path so the GUI can create a matching logbook.

Logger does not decide when logging starts or stops.

### `logbook.py`

Creates a human-readable text file paired with the CSV file.

It stores:

- Experiment information
- Sample
- Gas
- Operator
- General notes
- Timestamped events
- Session start and end times

The logbook is independent of the measurement CSV.

### `GUI/gui.py`

Controls the user workflow:

- Start and stop acquisition
- Start and stop logging
- Collect run information
- Add timestamped events
- Open configuration and help

The GUI does not communicate directly with instruments.

### `GUI/sensor_panel.py`

Displays the latest value and connection status for each measurement.

### `GUI/plot_panel.py`

Creates plots automatically from History columns. It also manages plot pinning, visible time windows, and export of the displayed History range.

### `GUI/gui_configuration.py`

Edits `config.json`, including sensor enable state, COM port, nickname, acquisition period, title, and logging directory.

### `auto_mode.py`

Provides a non-GUI way to run OpenLabDAQ. It can be used as a backup if the graphical interface cannot be started, or when the user prefers unattended acquisition without the GUI. It uses the same `daq.py`, sensor drivers, History, and Logger as the graphical interface.

When executed, it:

- Loads `config.json`
- Initializes and connects all enabled sensors
- Starts acquisition immediately
- Saves measurements automatically
- Continues running until stopped by the user


### `test_sensor.py`

Applies the standard driver lifecycle test:

```text
create → connect → read → disconnect → confirm read fails
```

## Design Rules

- One clear responsibility per module
- Only sensor drivers know instrument protocols
- Only `daq.py` talks to sensor drivers
- The GUI reads data from History
- Configuration is the source of experiment-dependent settings
- History is temporary; Logger is permanent
- Sensor drivers return values or raise clear exceptions
- Adding a sensor should not require changes to the DAQ backbone
