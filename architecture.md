# Tube Furnace DAQ Architecture

## Purpose

The Tube Furnace DAQ is designed to acquire measurements from multiple laboratory instruments using a simple, modular architecture.

The system separates the responsibilities of communication, data acquisition, temporary storage, permanent storage, and visualization into independent modules.

Each module has a single responsibility and communicates through well-defined interfaces.

---

# Overall Architecture

```
             config.json
                  │
                  ▼
              config.py
                  │
                  ▼
               main.py
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
  Sensor 1    Sensor 2    Sensor N
                  │
                  ▼
        Acquisition Record
                  │
         ┌────────┴────────┐
         ▼                 ▼
    history.py        logger.py
                           │
                           ▼
                          CSV

                  │
                  ▼
               gui.py
```

---

# Module Responsibilities

## config.json

Contains all experiment-dependent settings.

Examples include

- Communication ports
- Acquisition period
- Logging directory
- Enabled sensors

Changing experiments should only require modifying this file.

---

## config.py

Loads the configuration file and provides access to its contents.

---

## Sensor Drivers

Each sensor driver communicates with one physical instrument.

Its purpose is to translate the instrument's native communication protocol into the standard DAQ interface.

Every sensor driver follows the communication standard defined in **Sensor_Driver_Guide.md**.

---

## main.py

The main program coordinates the entire DAQ.

Responsibilities

- Read the configuration.
- Initialize enabled sensors.
- Control the acquisition timing.
- Request one measurement from every enabled sensor.
- Generate one timestamp per acquisition cycle.
- Assemble one acquisition record.
- Send the acquisition record to the History module.
- Send the acquisition record to the Logger module.

The main program does not know how any individual instrument communicates.

---

## history.py

Stores recent acquisition records in RAM.

Purpose

Provide fast access to recent data for visualization.

History is temporary storage only.

---

## logger.py

Writes acquisition records to permanent CSV files.

Logger is responsible only for permanent storage.

---

## gui.py

Displays the current state of the experiment.

The GUI reads acquisition records but does not communicate directly with sensors.

---

# Acquisition Cycle

During every acquisition period, the DAQ performs the following sequence.

1. Wait until the next acquisition period.
2. Generate the current timestamp.
3. Read every enabled sensor.
4. Assemble one acquisition record.
5. Send the acquisition record to History.
6. Send the acquisition record to Logger.
7. Repeat.

---

# Acquisition Record

One acquisition record represents one acquisition cycle.

It contains

- Timestamp
- One measurement from every enabled sensor

Example

| Timestamp | FurnaceTC (°C) | BusyBee (Torr) | Hornet (Torr) |
| ---------- | -------------- | -------------- | ------------- |
| 12:00:00 | 1000.2 | 0.52 | 0.48 |

The acquisition record is the standard data format exchanged between the DAQ backbone modules.

---

# Design Philosophy

The Tube Furnace DAQ follows the following principles.

- One responsibility per module.
- Simple, explicit architecture.
- Experiment settings belong in `config.json`.
- Sensor drivers translate instrument protocols into the standard DAQ interface.
- The backbone should not require modification when experiments change.
- Every module should be independently testable.
- Communication between modules should use well-defined interfaces.