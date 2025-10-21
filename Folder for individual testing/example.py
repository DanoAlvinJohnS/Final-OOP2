from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QDialog, QLabel, QLineEdit, QVBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
import sys


class GradeInputDialog(QDialog):
    grade_entered = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Grade")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """)

        layout = QVBoxLayout(self)

        instructions = QLabel(
            "Enter your grades for each course/trait below.\n"
            "- You can enter a percentage (0–100) or a decimal (0–1).\n"
            "- Press Enter to skip a feature (defaults to 0)."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Input your grade...")
        layout.addWidget(self.input_field)

        # Capture Enter key press
        self.input_field.returnPressed.connect(self.on_enter)

    def on_enter(self):
        text = self.input_field.text().strip()
        if not text:
            value = 0.0
        else:
            try:
                value = float(text)
                if value > 1:
                    value = min(value, 100)
            except ValueError:
                value = 0.0

        self.grade_entered.emit(value)
        self.accept()


class GradesTable(QWidget):
    data_updated = pyqtSignal(dict)  # emit updated data to GUI

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Course / Trait", "Grade"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.layout().addWidget(self.table)

        # Load initial data
        self.load_data(data)

        # Connect click signal
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)

    def load_data(self, data):
        """Load data = [{'course': 'Math', 'grade': None}, ...]"""
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            name_item = QTableWidgetItem(entry["course"])
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            grade_text = "" if entry.get("grade") is None else str(entry["grade"])
            grade_item = QTableWidgetItem(grade_text)
            self.table.setItem(row, 1, grade_item)

            self.update_row_color(row, entry.get("grade"))

    def update_row_color(self, row, grade):
        """Change row color based on grade status."""
        for col in range(2):
            item = self.table.item(row, col)
            if not item:
                continue

            if grade is None:
                color = QColor(255, 255, 255)  # white
            elif grade == "selected":
                color = QColor(230, 230, 230)  # gray highlight
            else:
                color = QColor(200, 255, 200)  # light green for filled

            item.setBackground(QBrush(color))

    def on_cell_clicked(self, row, column):
        """Open dialog when clicking grade cell."""
        if column != 1:
            return

        # Highlight active row
        self.update_row_color(row, "selected")

        dialog = GradeInputDialog(self)
        dialog.grade_entered.connect(lambda val: self.set_grade(row, val))
        dialog.exec()

    def set_grade(self, row, grade):
        """Set grade and update color."""
        self.table.item(row, 1).setText(str(grade))
        self.update_row_color(row, grade)

        # emit current table data to parent GUI
        current_data = {}
        for r in range(self.table.rowCount()):
            course = self.table.item(r, 0).text()
            grade_text = self.table.item(r, 1).text().strip()
            grade_val = float(grade_text) if grade_text else 0.0
            current_data[course] = grade_val

        self.data_updated.emit(current_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    data = [
        {"course": "Mathematics", "grade": None},
        {"course": "Programming Fundamentals", "grade": None},
        {"course": "Embedded Systems", "grade": None},
        {"course": "IoT Architecture", "grade": None},
        {"course": "Data Structures", "grade": None},
    ]

    win = GradesTable(data)
    win.resize(600, 400)
    win.show()

    sys.exit(app.exec())
