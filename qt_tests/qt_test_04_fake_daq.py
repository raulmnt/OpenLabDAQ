import sys
import random

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from PySide6.QtCore import QTimer


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tube Furnace DAQ")

        self.logging = False

        self.temp_label = QLabel("Furnace: ---- °C")
        self.pressure_label = QLabel("Pressure: ---- Torr")
        self.logging_label = QLabel("Logging: OFF")

        self.button = QPushButton("Start / Stop Logging")
        self.button.clicked.connect(self.toggle_logging)

        layout = QVBoxLayout()

        layout.addWidget(self.temp_label)
        layout.addWidget(self.pressure_label)
        layout.addWidget(self.logging_label)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def update_data(self):

        temperature = random.uniform(995,1005)
        pressure = random.uniform(0.001,0.005)

        self.temp_label.setText(
            f"Furnace: {temperature:.1f} °C"
        )

        self.pressure_label.setText(
            f"Pressure: {pressure:.4f} Torr"
        )

        if self.logging:
            print(
                temperature,
                pressure
            )

    def toggle_logging(self):

        self.logging = not self.logging

        if self.logging:
            self.logging_label.setText("Logging: ON")
        else:
            self.logging_label.setText("Logging: OFF")


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())