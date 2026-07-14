"""
GUI/gui.py

Main graphical interface for OpenLabDAQ.

Operation
---------
- The application name remains OpenLabDAQ.
- The large system title is loaded from config.json.
- Saving the configuration updates the title and sensor nicknames.
- RUN connects the DAQ and starts continuous acquisition.
- STOP disconnects the DAQ.
- LOAD starts CSV logging.
- LOGGING stops CSV logging.
- All displayed measurements are read only from History.
- Sensor nicknames affect only the GUI.
"""

import sys
from pathlib import Path
from PySide6.QtGui import QIcon
import ctypes

# Allow this file to import modules from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ICON_FILE = PROJECT_ROOT / "assets" / "OpenLabDAQ.ico"
APP_ID = "OpenLab.OpenLabDAQ.1.0"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import load_config
from daq import DAQ
from GUI.gui_configuration import ConfigurationWindow
from GUI.help import HelpWindow
from GUI.plot_panel import PlotPanel
from GUI.sensor_panel import SensorPanel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Initial GUI states.
        self.daq = None
        self.running = False
        self.logging_active = False

        self.configuration_window = None
        self.help_window = None

        # Timer responsible for continuous acquisition.
        self.acquisition_timer = QTimer(self)
        self.acquisition_timer.timeout.connect(self.acquire_data)

        # The application identity always remains OpenLabDAQ.
        self.setWindowTitle("OpenLabDAQ")
        self.resize(1600, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        self.create_header()
        self.create_body()

    # ---------------------------------------------------------
    # Layout
    # ---------------------------------------------------------

    def create_header(self):

        header_layout = QHBoxLayout()

        # User-defined title for the experimental system.
        self.title_label = QLabel(
            self.get_display_title()
        )
        self.title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
        """)

        self.configuration_button = QPushButton(
            "Configuration"
        )
        self.configuration_button.setMinimumHeight(45)
        self.configuration_button.setStyleSheet("""
            font-size: 16px;
        """)
        self.configuration_button.setToolTip(
            "Open the DAQ configuration."
        )
        self.configuration_button.clicked.connect(
            self.configuration_pressed
        )

        self.help_button = QPushButton("Help")
        self.help_button.setMinimumHeight(45)
        self.help_button.setStyleSheet("""
            font-size: 16px;
        """)
        self.help_button.setToolTip(
            "Click to view instructions."
        )
        self.help_button.clicked.connect(
            self.help_pressed
        )

        header_layout.addStretch()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(
            self.configuration_button
        )
        header_layout.addWidget(self.help_button)

        self.main_layout.addLayout(header_layout)

    def create_body(self):

        body_layout = QHBoxLayout()

        left_panel = QWidget()
        left_panel.setFixedWidth(350)

        left_layout = QVBoxLayout(left_panel)

        # Initial DAQ state.
        self.run_button = QPushButton(
            "STOPPED"
        )
        self.run_button.setMinimumHeight(70)
        self.run_button.setStyleSheet(
            self.stopped_style()
        )
        self.run_button.setToolTip(
            "Click to start acquisition."
        )
        self.run_button.clicked.connect(
            self.run_pressed
        )

        # Initial logging state.
        self.logging_button = QPushButton("LOAD")
        self.logging_button.setMinimumHeight(70)
        self.logging_button.setStyleSheet(
            self.load_style()
        )
        self.logging_button.setToolTip(
            "Start acquisition before saving data."
        )
        self.logging_button.clicked.connect(
            self.logging_pressed
        )

        sensor_nicknames = self.get_sensor_nicknames()

        self.sensor_panel = SensorPanel(
            sensor_nicknames
        )
        self.plot_panel = PlotPanel(
            sensor_nicknames
        )

        left_layout.addWidget(self.run_button)
        left_layout.addWidget(self.logging_button)
        left_layout.addSpacing(30)
        left_layout.addWidget(self.sensor_panel)

        body_layout.addWidget(left_panel)
        body_layout.addWidget(self.plot_panel)

        self.main_layout.addLayout(body_layout)

    # ---------------------------------------------------------
    # Display configuration
    # ---------------------------------------------------------

    @staticmethod
    def get_display_title():
        """
        Read the user-defined system title from config.json.
        """

        config = load_config()

        return config.get(
            "display",
            {},
        ).get(
            "title",
            "OpenLabDAQ",
        )

    @staticmethod
    def get_sensor_nicknames():
        """
        Read optional display-only sensor nicknames.
        """

        config = load_config()

        return {
            sensor_name: str(
                settings.get(
                    "nickname",
                    "",
                )
                or ""
            ).strip()
            for sensor_name, settings in config.get(
                "sensors",
                {},
            ).items()
        }

    def reload_display_configuration(self):
        """
        Reload the system title and sensor nicknames after Save.
        """

        self.title_label.setText(
            self.get_display_title()
        )

        sensor_nicknames = (
            self.get_sensor_nicknames()
        )

        self.sensor_panel.set_sensor_nicknames(
            sensor_nicknames
        )
        self.plot_panel.set_sensor_nicknames(
            sensor_nicknames
        )

    # ---------------------------------------------------------
    # DAQ control
    # ---------------------------------------------------------

    def run_pressed(self):

        if self.running:
            self.stop_daq()
        else:
            self.start_daq()

    def start_daq(self):
        """
        Display the connection message before beginning the
        blocking sensor connection process.
        """

        # Reload nicknames in case config.json was edited externally.
        self.reload_display_configuration()

        self.sensor_panel.set_connecting()

        self.run_button.setEnabled(False)
        self.run_button.setToolTip(
            "Connecting sensors..."
        )

        # Allow Qt to repaint before sensor connection begins.
        QTimer.singleShot(50, self.connect_daq)

    def connect_daq(self):
        """
        Create and connect the DAQ.
        """

        try:
            self.daq = DAQ()

            # GUI logging begins disabled.
            self.daq.stop_logging()

            self.daq.connect()

        except Exception as error:

            self.cleanup_failed_start()

            self.run_button.setEnabled(True)
            self.run_button.setText(
                "STOPPED"
            )
            self.run_button.setStyleSheet(
                self.stopped_style()
            )
            self.run_button.setToolTip(
                "Click to start acquisition."
            )

            self.configuration_button.setEnabled(
                True
            )
            self.configuration_button.setToolTip(
                "Open the DAQ configuration."
            )

            self.sensor_panel.set_stopped()

            QMessageBox.critical(
                self,
                "DAQ Connection Error",
                str(error),
            )

            return

        self.running = True

        self.run_button.setEnabled(True)
        self.run_button.setText(
            "RUNNING"
        )
        self.run_button.setStyleSheet(
            self.running_style()
        )
        self.run_button.setToolTip(
            "Click to stop acquisition."
        )

        self.logging_button.setToolTip(
            "Click to start saving data."
        )

        # Configuration cannot change while the DAQ is active.
        self.configuration_button.setEnabled(False)
        self.configuration_button.setToolTip(
            "Stop acquisition before changing the configuration."
        )

        # Acquire immediately before starting the timer.
        self.acquire_data()

        if not self.running:
            return

        period_ms = max(
            1,
            round(self.daq.period * 1000),
        )

        self.acquisition_timer.start(period_ms)

    def acquire_data(self):
        """
        Perform one acquisition and update the GUI from History.
        """

        if not self.running or self.daq is None:
            return

        try:
            self.daq.acquire_once()

        except Exception as error:

            self.stop_daq()

            QMessageBox.critical(
                self,
                "Acquisition Error",
                str(error),
            )

            return

        # Display components read only from History.
        self.sensor_panel.update_from_history(
            self.daq.history
        )

        self.plot_panel.update_from_history(
            self.daq.history
        )

    def stop_daq(self):
        """
        Stop acquisition and disconnect all sensors.
        """

        self.acquisition_timer.stop()

        if self.daq is not None:

            try:
                self.daq.disconnect()

            except Exception as error:

                QMessageBox.warning(
                    self,
                    "DAQ Disconnection Error",
                    str(error),
                )

        self.daq = None
        self.running = False
        self.logging_active = False

        self.run_button.setEnabled(True)
        self.run_button.setText(
            "STOPPED\n(Click to Run)"
        )
        self.run_button.setStyleSheet(
            self.stopped_style()
        )
        self.run_button.setToolTip(
            "Click to start acquisition."
        )

        self.logging_button.setText("LOAD")
        self.logging_button.setStyleSheet(
            self.load_style()
        )
        self.logging_button.setToolTip(
            "Start acquisition before saving data."
        )

        self.configuration_button.setEnabled(True)
        self.configuration_button.setToolTip(
            "Open the DAQ configuration."
        )

        # Keep the last values visible with gray status dots.
        self.sensor_panel.set_stopped()

    def cleanup_failed_start(self):
        """
        Clean up after an unsuccessful DAQ connection.
        """

        self.acquisition_timer.stop()

        if self.daq is not None:

            try:
                self.daq.disconnect()

            except Exception:
                pass

        self.daq = None
        self.running = False
        self.logging_active = False

    # ---------------------------------------------------------
    # Logging control
    # ---------------------------------------------------------

    def logging_pressed(self):
        """
        Start or stop CSV logging.
        """

        if not self.running or self.daq is None:
            return

        if self.logging_active:

            self.daq.stop_logging()

            self.logging_active = False

            self.logging_button.setText("LOAD")
            self.logging_button.setStyleSheet(
                self.load_style()
            )
            self.logging_button.setToolTip(
                "Click to start saving data."
            )

        else:

            self.daq.start_logging()

            self.logging_active = True

            self.logging_button.setText("LOGGING")
            self.logging_button.setStyleSheet(
                self.logging_style()
            )
            self.logging_button.setToolTip(
                "Click to stop saving data."
            )

    # ---------------------------------------------------------
    # Other controls
    # ---------------------------------------------------------

    def configuration_pressed(self):
        """
        Open the configuration window.

        Display labels are refreshed when the user clicks Save.
        """

        self.configuration_window = ConfigurationWindow()

        self.configuration_window.accepted.connect(
            self.reload_display_configuration
        )

        self.configuration_window.show()

    def help_pressed(self):

        self.help_window = HelpWindow()
        self.help_window.show()

    # ---------------------------------------------------------
    # Styles
    # ---------------------------------------------------------

    @staticmethod
    def stopped_style():

        return """
            font-size: 20px;
            font-weight: bold;
            background-color: #b94a48;
            color: white;
        """

    @staticmethod
    def running_style():

        return """
            font-size: 20px;
            font-weight: bold;
            background-color: #3c9a5f;
            color: white;
        """

    @staticmethod
    def load_style():

        return """
            font-size: 20px;
            font-weight: bold;
            background-color: #b94a48;
            color: white;
        """

    @staticmethod
    def logging_style():

        return """
            font-size: 20px;
            font-weight: bold;
            background-color: #3c9a5f;
            color: white;
        """

    # ---------------------------------------------------------
    # Safe shutdown
    # ---------------------------------------------------------

    def closeEvent(self, event):

        if self.running:
            self.stop_daq()

        event.accept()


def main():

    # Tell Windows this is OpenLabDAQ, not the Python interpreter.
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_ID
        )

    app = QApplication(sys.argv)

    icon = QIcon(str(ICON_FILE))

    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()