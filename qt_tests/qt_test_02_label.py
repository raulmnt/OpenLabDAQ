import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.label = QLabel("Logging OFF")

        button = QPushButton("Start Logging")
        button.clicked.connect(self.start_logging)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(button)

        self.setLayout(layout)

    def start_logging(self):
        self.label.setText("Logging ON")
        print("Start logging")


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())