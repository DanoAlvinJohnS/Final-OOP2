import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "PyQt6 Login Screen"
        self.x = 200   # left
        self.y = 200   # top
        self.width = 300
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.x, self.y, self.width, self.height)
        self.setWindowIcon(QIcon("pythonico.ico"))  # optional icon
        self.createGridLayout()
        self.setLayout(self.layout)
        self.show()

    def createGridLayout(self):
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 2)

        # Username label and input
        self.textboxlbl = QLabel("Username:", self)
        self.textbox = QLineEdit(self)

        # Password label and input
        self.passwordlbl = QLabel("Password:", self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        # Register button
        self.button = QPushButton("Register", self)
        self.button.setToolTip("You've hovered over me!")

        # Add widgets to the layout (row, column)
        self.layout.addWidget(self.textboxlbl, 0, 1)
        self.layout.addWidget(self.textbox, 0, 2)
        self.layout.addWidget(self.passwordlbl, 1, 1)
        self.layout.addWidget(self.password, 1, 2)
        self.layout.addWidget(self.button, 2, 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
