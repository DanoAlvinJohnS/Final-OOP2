import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QMenuBar, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Calculator")
        self.setGeometry(300, 200, 350, 400)
        self.history_file = "calc_history.txt"
        self.createUI()

    def createUI(self):
        main_layout = QVBoxLayout()

        # Menu Bar
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open History", self)
        open_action.triggered.connect(self.open_history)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        main_layout.setMenuBar(menu_bar)

        # Display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 20px; padding: 8px;")
        main_layout.addWidget(self.display)

        # Button layout
        buttons = [
            ['7', '8', '9', '/', 'sin'],
            ['4', '5', '6', '*', 'cos'],
            ['1', '2', '3', '-', 'exp'],
            ['0', '.', 'C', '+', '=']
        ]

        grid = QGridLayout()
        for r, row in enumerate(buttons):
            for c, text in enumerate(row):
                btn = QPushButton(text)
                btn.setFixedSize(60, 60)
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        background-color: #ececec;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #b3e0ff;
                    }
                """)
                btn.clicked.connect(self.on_button_click)
                grid.addWidget(btn, r, c)
        main_layout.addLayout(grid)

        self.setLayout(main_layout)

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == 'C':
            self.display.clear()
        elif text == '=':
            self.calculate_result()
        elif text in ['sin', 'cos', 'exp']:
            self.apply_function(text)
        else:
            self.display.setText(self.display.text() + text)

    def calculate_result(self):
        try:
            expression = self.display.text()
            result = str(eval(expression))
            self.display.setText(result)
            self.save_to_history(expression, result)
        except Exception:
            self.display.setText("Error")

    def apply_function(self, func):
        try:
            value = float(self.display.text())
            if func == 'sin':
                result = str(round(math.sin(math.radians(value)), 6))
            elif func == 'cos':
                result = str(round(math.cos(math.radians(value)), 6))
            elif func == 'exp':
                result = str(round(math.exp(value), 6))
            self.display.setText(result)
            self.save_to_history(f"{func}({value})", result)
        except Exception:
            self.display.setText("Error")

    def save_to_history(self, expr, res):
        with open(self.history_file, "a") as file:
            file.write(f"{expr} = {res}\n")

    def open_history(self):
        try:
            with open(self.history_file, "r") as file:
                content = file.read()
            QMessageBox.information(self, "Calculation History", content)
        except FileNotFoundError:
            QMessageBox.warning(self, "History", "No history file found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
