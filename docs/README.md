# Tube Furnace DAQ

A modular Python-based data acquisition (DAQ) system for a laboratory tube furnace and associated instrumentation.

## Project Goals

- Modular architecture.
- One responsibility per file.
- Easy to expand with new sensors.
- Human-readable CSV data.
- Simple and maintainable code.

## Current Status

The project is under active development.

Current completed modules include:

- Configuration management
- FurnaceTC sensor driver
- History module
- Standard sensor driver interface
- Standard sensor driver acceptance test

## Documentation

Project documentation is located in the `docs/` directory.

- `Architecture.md` — Overall software architecture.
- `Sensor_Driver_Guide.md` — Standard interface for developing new sensor drivers.

## Repository Structure

```
TubeFurnaceDAQ/
│
├── docs/
├── sensors/
├── config.py
├── config.json
├── history.py
├── logger.py
├── main.py
├── gui.py
└── test_sensor.py
```

## License

This project is intended for research and educational use.