"""
logger.py

Provides permanent storage of acquisition records.

Responsibilities
----------------
- Create a new CSV file.
- Write the CSV header.
- Append acquisition records.

The Logger does not decide when data should be saved.
That responsibility belongs to the DAQ backbone (main.py).
"""

from pathlib import Path
from datetime import datetime
import csv


class Logger:
    """
    Writes acquisition records to CSV files.
    """

    def __init__(self, directory):
        """
        Create a Logger object.

        Parameters
        ----------
        directory : str
            Directory where log files will be stored.
        """

        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

        self.file = None
        self.writer = None

    def new_file(self, record):
        """
        Create a new CSV file.

        Parameters
        ----------
        record : dict
            First acquisition record.
            Used to generate the CSV header.
        """

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")

        filepath = self.directory / filename

        self.file = open(filepath, "w", newline="")

        self.writer = csv.DictWriter(
            self.file,
            fieldnames=record.keys()
        )

        self.writer.writeheader()

    def write(self, record):
        """
        Append one acquisition record to the CSV file.

        Parameters
        ----------
        record : dict
            Acquisition record.
        """

        if self.writer is None:
            raise RuntimeError("No log file is currently open.")

        self.writer.writerow(record)

        # Immediately save to disk.
        self.file.flush()

    def close(self):
        """
        Close the current CSV file.
        """

        if self.file is not None:
            self.file.close()
            self.file = None
            self.writer = None