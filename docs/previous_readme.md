# TubeFurnaceDAQ
Modular Python data acquisition software for a high-temperature tube furnace.
## Sensor Communication Protocol

To ensure a consistent and modular architecture, all Arduino-based sensors in the Tube Furnace DAQ project must follow the same serial communication protocol.

### General Rules

- Every line transmitted over the serial port represents **exactly one measurement**.
- Sensors continuously stream measurements while connected.
- No startup messages, debug messages, or status text are transmitted.
- The Arduino is responsible only for acquiring and transmitting measurements.
- Python is responsible for timestamps, connection management, plotting, history, and data logging.

### Data Format

Each measurement is transmitted as a single comma-separated line:

```text
SensorName,Value,Unit
```

Examples:

```text
MicroBee,12.3456,Torr
FurnaceTC,998.4,C
FlowController,25.0,sccm
```

### Purpose

Using a common communication format allows each Python sensor class to:

- Automatically identify its corresponding device.
- Parse measurements using the same logic.
- Remain independent from other sensors.
- Simplify future expansion of the DAQ system.