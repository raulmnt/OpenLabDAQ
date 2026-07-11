import sys
from PySide6.QtWidgets import QApplication, QPushButton


def start_logging():
    print("Start logging command received")


app = QApplication(sys.argv)

button = QPushButton("Start Logging")
button.clicked.connect(start_logging)
button.resize(250, 80)
button.show()

sys.exit(app.exec())