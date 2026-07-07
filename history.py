"""
history.py

Temporary in-memory storage for DAQ measurements.

The History class stores recent Measurement objects so the GUI can display
recent data without reading from the CSV log file.
"""

from collections import deque
from datetime import timedelta

from config import load_config


class History:
    """
    Store recent Measurement objects in RAM.

    History is temporary storage. It is mainly intended for plotting recent
    data in the GUI. Permanent storage is handled separately by logger.py.
    """

    def __init__(self):
        """
        Create an empty history buffer.

        The retention time is read from config.json:

            "history": {
                "retention_hours": 24
            }
        """
        config = load_config()

        self.retention_hours = config["history"]["retention_hours"]
        self.retention_time = timedelta(hours=self.retention_hours)

        # A deque is like a list, but it is efficient for removing items
        # from the beginning. This is useful because History adds new
        # measurements at the end and removes old measurements from the start.
        self.measurements = deque()

    def add(self, measurement):
        """
        Add a new Measurement object to history.

        Old measurements outside the retention time are removed automatically.
        """
        self.measurements.append(measurement)
        self._remove_old_measurements()

    def get_all(self):
        """
        Return all measurements currently stored in history.

        Returns
        -------
        list
            A list of Measurement objects.
        """
        return list(self.measurements)

    def get_latest(self):
        """
        Return the most recent Measurement object.

        Returns
        -------
        Measurement or None
            The newest measurement, or None if history is empty.
        """
        if not self.measurements:
            return None

        return self.measurements[-1]

    def clear(self):
        """
        Remove all measurements from history.
        """
        self.measurements.clear()

    def _remove_old_measurements(self):
        """
        Remove measurements older than the configured retention time.

        This is a private helper method. It is only used internally by History.
        """
        if not self.measurements:
            return

        newest_time = self.measurements[-1].timestamp
        cutoff_time = newest_time - self.retention_time

        while self.measurements and self.measurements[0].timestamp < cutoff_time:
            self.measurements.popleft()