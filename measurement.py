
"""
measurement.py

Defines the Measurement class used throughout the Tube Furnace DAQ.

A Measurement represents a single sensor reading and contains:
- Sensor name
- Measured value
- Measurement unit
- Timestamp

All sensor classes return Measurement objects so that the rest of
the software (GUI, history, logger, etc.) can work with a common format.

The class also provides helper methods for representing a measurement
in standard formats, such as a CSV row. It does not perform any file
input/output; saving measurements is handled by logger.py.
"""

# Import the dataclass decorator to simplify creation of data-only classes.
from dataclasses import dataclass
# Import datetime so measurements can be timestamped.
from datetime import datetime


@dataclass(frozen=True)
class Measurement:
    name: str
    value: float
    unit: str
    timestamp: datetime

    """
    Convert the measurement into a list suitable for writing
    as one row in a CSV file.
    """
    def to_csv_row(self) -> list:
        return [
            self.timestamp.isoformat(),
            self.name,
            self.value,
            self.unit,
        ]