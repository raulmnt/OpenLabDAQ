# OpenLabDAQ

OpenLabDAQ is a modular Python data-acquisition program for laboratory instruments.

It connects multiple sensors, displays live values and plots, keeps recent data in memory, and saves synchronized measurements to CSV files. New instruments are added through independent sensor drivers without redesigning the DAQ, logger, history, or GUI.

## Main Features

- Configuration-driven sensor loading
- Live sensor values and one plot per measurement
- Optional display nicknames for sensors
- Selectable plot history from 5 minutes to 3 days
- CSV logging with synchronized timestamps
- Run metadata and timestamped event logbooks
- Export of the currently displayed History range
- GUI and non-GUI operation
- Standard driver interface and acceptance test

## Quick Start

1. Install the required Python packages.
2. Add and test the required sensor drivers following the
   [Sensor Driver Guide](docs/Sensor_Driver_Guide.md).
3. Configure the enabled sensors, COM ports, acquisition period, and saving directory.
4. Run OpenLabDAQ using either the graphical interface or `auto_mode.py`.

Detailed setup and operating instructions are available in 
[Getting Started] (docs/Getting_Started.md)

## Repository Structure

```text
OpenLabDAQ/
├── assets/                 Application icon and other assets
├── Data/                   Default output directory
├── docs/
│   ├── architecture.md
│   └── Sensor_Driver_Guide.md
├── GUI/
│   ├── gui.py
│   ├── gui_configuration.py
│   ├── help.py
│   ├── help_content.html
│   ├── plot_panel.py
│   ├── sensor_panel.py
│   └── styles.py
├── sensors/                Instrument drivers
├── auto_mode.py            Non-GUI operation
├── config.json             User configuration
├── config.py               Configuration loading and saving
├── daq.py                  DAQ backbone
├── history.py              Temporary in-memory records
├── logbook.py              Run metadata and event log
├── logger.py               CSV writer
├── test_sensor.py          Standard driver acceptance test
├── requirements.txt
├── OpenLabDAQ.bat
└── OpenLabDAQ_Debug.bat
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — software structure and data flow
- [`docs/Sensor_Driver_Guide.md`](docs/Sensor_Driver_Guide.md) — requirements for adding instruments
- `GUI/help_content.html` — user instructions shown inside OpenLabDAQ

## Project Status

The core architecture and user interface are complete. Future development is expected to focus mainly on additional sensor drivers, documentation, and optional integrations such as selected-mass RGA data streams.
