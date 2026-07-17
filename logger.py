"""
logger.py

Provides permanent storage of acquisition records.

Responsibilities
----------------
- Create a new CSV file.
- Write the CSV header.
- Append acquisition records.
- Expose the path of the CSV file most recently created.

The Logger does not decide when data should be saved.
That responsibility belongs to the DAQ backbone.
"""

import csv
from datetime import datetime
from pathlib import Path


class Logger:
    """
    Write acquisition records to CSV files.
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
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.file = None
        self.writer = None

        # Path of the CSV file most recently created by new_file().
        # This lets the GUI create a matching session-log filename
        # without changing how CSV logging works.
        self.file_path = None

    def new_file(self, record):
        """
        Create a new CSV file and write its header.

        Parameters
        ----------
        record : dict
            First acquisition record. Its keys define the CSV columns.
        """

        filename = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S.csv"
        )

        self.file_path = self.directory / filename

        self.file = open(
            self.file_path,
            "w",
            newline="",
            encoding="utf-8",
        )

        self.writer = csv.DictWriter(
            self.file,
            fieldnames=record.keys(),
        )

        self.writer.writeheader()

        # Save the header immediately.
        self.file.flush()

    def write(self, record):
        """
        Append one acquisition record to the current CSV file.

        Parameters
        ----------
        record : dict
            Acquisition record.
        """

        if self.writer is None:
            raise RuntimeError(
                "No log file is currently open."
            )

        self.writer.writerow(record)

        # Immediately save each record to disk.
        self.file.flush()

    def close(self):
        """
        Close the current CSV file.

        file_path is intentionally preserved so other parts of the
        application can still identify the file that was just written.
        """

        if self.file is not None:
            self.file.close()

        self.file = None
        self.writer = None
