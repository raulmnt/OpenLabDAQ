import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.counter = 0

        self.label = QLabel("0")

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_counter)
        self.timer.start(1000)

    def update_counter(self):
        self.counter += 1
        self.label.setText(str(self.counter))
        print(self.counter)


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())