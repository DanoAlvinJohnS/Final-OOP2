import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QLinearGradient, QBrush, QPalette, QColor
from PyQt6.QtCore import Qt


class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculation History")
        self.setFixedWidth(200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
            QTextEdit {
                background: white;
                border: none;
                color: black;
                font-size: 13px;
                padding: 8px;
            }
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4b4b;
            }
        """)
        self.layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedWidth(30)
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.text_area)
        self.setLayout(self.layout)

    def add_entry(self, entry):
        self.text_area.append(entry)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.history_window = None
        self.drag_position = None
        self.setFixedSize(350, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 540)
        gradient.setColorAt(0.0, QColor("#e8ffe9"))
        gradient.setColorAt(1.0, QColor("#ccfbd1"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(60)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("""
            QLineEdit {
                background: white;
                color: black;
                border-radius: 8px;
                font-size: 20px;
                padding-right: 10px;
            }
        """)
        vbox.addWidget(self.display)

        self.top_buttons = QGridLayout()
        self.min_btn = QPushButton("-")
        self.close_btn = QPushButton("X")
        for btn, color in [(self.min_btn, "#fbc02d"), (self.close_btn, "#e53935")]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: none;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #212121;
                }}
            """)
        self.min_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)
        self.top_buttons.addWidget(self.min_btn, 0, 0)
        self.top_buttons.addWidget(self.close_btn, 0, 1)
        vbox.addLayout(self.top_buttons)

        grid = QGridLayout()
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '+', '='],
            ['sin', 'cos', 'exp', ''],
            ['C', '⌫', '', '']
        ]

        for row, row_data in enumerate(buttons):
            for col, text in enumerate(row_data):
                if not text:
                    continue
                button = QPushButton(text)
                button.setFixedSize(70, 50)
                if text in '0123456789.':
                    button.setStyleSheet("""
                        QPushButton {
                            background: white;
                            color: black;
                            border-radius: 6px;
                            font-size: 16px;
                        }
                        QPushButton:hover { background: #e0e0e0; }
                    """)
                elif text == '=':
                    button.setStyleSheet("""
                        QPushButton {
                            background: #66bb6a;
                            border: 2px solid green;
                            color: white;
                            font-size: 18px;
                            border-radius: 6px;
                        }
                        QPushButton:hover { background: #4caf50; }
                    """)
                elif text == 'C':
                    button.setStyleSheet("""
                        QPushButton {
                            background: #ffb74d;
                            color: white;
                            border-radius: 6px;
                            font-size: 15px;
                        }
                        QPushButton:hover { background: #ffa726; }
                    """)
                elif text == '⌫':
                    button.setStyleSheet("""
                        QPushButton {
                            background: #b0bec5;
                            color: black;
                            border-radius: 6px;
                            font-size: 15px;
                        }
                        QPushButton:hover { background: #90a4ae; }
                    """)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background: #a5d6a7;
                            color: black;
                            border-radius: 6px;
                            font-size: 15px;
                        }
                        QPushButton:hover { background: #81c784; }
                    """)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col)
        vbox.addLayout(grid)
        self.setLayout(vbox)

    def on_click(self):
        button = self.sender()
        text = button.text()
        current = self.display.text()

        if text == "C":
            self.display.clear()
        elif text == "⌫":
            self.display.setText(current[:-1])
        elif text == "=":
            try:
                expression = self.display.text()
                if self.has_duplicate_operators(expression):
                    raise Exception("Invalid expression")
                result = str(eval(expression))
                self.display.setText(result)
                self.save_to_history(expression, result)
            except Exception:
                QMessageBox.warning(self, "Error", "Invalid or malformed expression!", QMessageBox.StandardButton.Ok)
                self.display.setText("Error")
        elif text in ("sin", "cos", "exp"):
            try:
                val = float(self.display.text())
                result = {"sin": math.sin(val), "cos": math.cos(val), "exp": math.exp(val)}[text]
                self.display.setText(str(round(result, 5)))
                self.save_to_history(f"{text}({val})", result)
            except Exception:
                QMessageBox.warning(self, "Error", "Invalid input for function!", QMessageBox.StandardButton.Ok)
                self.display.setText("Error")
        else:
            if len(current) > 0 and current[-1] in "+-*/" and text in "+-*/":
                QMessageBox.warning(self, "Error", "Duplicate operator detected!", QMessageBox.StandardButton.Ok)
            else:
                self.display.setText(current + text)

    def has_duplicate_operators(self, expression):
        return any(op * 2 in expression for op in "+-*/")

    def save_to_history(self, expression, result):
        if not self.history_window:
            self.history_window = HistoryWindow()
            self.history_window.setGeometry(
                self.geometry().x() + self.width(),
                self.geometry().y(),
                200,
                self.height()
            )
        self.history_window.show()
        self.history_window.add_entry(f"{expression} = {result}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())
