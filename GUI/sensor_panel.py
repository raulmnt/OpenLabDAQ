"""
GUI/sensor_panel.py

Displays the latest value and connection status for every measurement
stored in History.

Sensor nicknames affect only the GUI. History and CSV column names remain
unchanged.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SensorPanel(QWidget):

    def __init__(self, sensor_nicknames=None):
        super().__init__()

        # Maps official sensor names to optional GUI nicknames.
        self.sensor_nicknames = dict(sensor_nicknames or {})

        self.sensor_rows = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.message_label = QLabel("No sensor data")
        self.message_label.setStyleSheet("""
            font-size: 22px;
        """)

        self.layout.addWidget(self.message_label)
        self.layout.addStretch()

    # ---------------------------------------------------------

    def set_sensor_nicknames(self, sensor_nicknames):
        """
        Replace the nickname mapping and refresh existing labels.
        """

        self.sensor_nicknames = dict(sensor_nicknames or {})

        for column, row in self.sensor_rows.items():
            self.update_name_label(
                row["name"],
                column,
            )

    # ---------------------------------------------------------

    def update_from_history(self, history):

        record = history.get_latest_record()

        if record is None:
            return

        measurement_columns = [
            column
            for column in record
            if column != "Timestamp"
        ]

        if set(measurement_columns) != set(self.sensor_rows):
            self.build_rows(measurement_columns)

        for column in measurement_columns:

            value = record[column]

            status_label = self.sensor_rows[column]["status"]
            value_label = self.sensor_rows[column]["value"]

            status_label.setStyleSheet("""
                color: green;
                font-size: 24px;
            """)

            value_label.setText(self.format_value(value))

    # ---------------------------------------------------------

    def build_rows(self, columns):

        self.clear_layout()

        self.sensor_rows = {}

        for column in columns:

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            name_layout = QHBoxLayout()

            status_label = QLabel("●")
            status_label.setStyleSheet("""
                color: gray;
                font-size: 24px;
            """)

            name_label = QLabel()
            name_label.setStyleSheet("""
                font-size: 22px;
                font-weight: bold;
            """)

            self.update_name_label(
                name_label,
                column,
            )

            value_label = QLabel("----")
            value_label.setStyleSheet("""
                font-size: 26px;
            """)

            name_layout.addWidget(status_label)
            name_layout.addWidget(name_label)
            name_layout.addStretch()

            container_layout.addLayout(name_layout)
            container_layout.addWidget(value_label)

            self.layout.addWidget(container)
            self.layout.addSpacing(20)

            self.sensor_rows[column] = {
                "status": status_label,
                "name": name_label,
                "value": value_label,
            }

        self.layout.addStretch()

    # ---------------------------------------------------------

    def set_connecting(self):
        """
        Show an immediate connection message while the DAQ connects.
        """

        self.clear_layout()
        self.sensor_rows = {}

        self.message_label = QLabel("Connecting sensors...")
        self.message_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)

        self.layout.addWidget(self.message_label)
        self.layout.addStretch()

    # ---------------------------------------------------------

    def set_stopped(self):

        for row in self.sensor_rows.values():

            row["status"].setStyleSheet("""
                color: gray;
                font-size: 24px;
            """)

    # ---------------------------------------------------------

    def update_name_label(self, label, column):
        """
        Apply the GUI nickname while preserving the unit suffix.
        """

        display_name = self.get_display_column_name(column)

        label.setText(display_name)

        if display_name != column:
            label.setToolTip(
                f"History and CSV name: {column}"
            )
        else:
            label.setToolTip("")

    # ---------------------------------------------------------

    def get_display_column_name(self, column):
        """
        Replace an official sensor name with its optional nickname.

        Example
        -------
        OmegaTC_1 (°C) -> Chamber Temperature (°C)
        """

        sensor_names = sorted(
            self.sensor_nicknames,
            key=len,
            reverse=True,
        )

        for sensor_name in sensor_names:

            is_exact_name = column == sensor_name
            has_unit_suffix = column.startswith(
                f"{sensor_name} ("
            )

            if not is_exact_name and not has_unit_suffix:
                continue

            nickname = str(
                self.sensor_nicknames.get(
                    sensor_name,
                    "",
                )
                or ""
            ).strip()

            if not nickname:
                return column

            suffix = column[len(sensor_name):]

            return f"{nickname}{suffix}"

        return column

    # ---------------------------------------------------------

    def clear_layout(self):

        while self.layout.count():

            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    # ---------------------------------------------------------

    @staticmethod
    def format_value(value):

        if isinstance(value, float):
            return f"{value:.4g}"

        return str(value)