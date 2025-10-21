import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLineEdit, QLabel
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIntValidator
from PyQt6.QtCore import Qt

_window_ref = None

from predict_compatibility import (
    load_all_specialization_models,
    union_all_features,
    generate_dummy_student,
    predict_all_compatibilities,
    save_results
)


class IntroWindow(QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Input Intro")
        self.setGeometry(200, 200, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top buttons
        top_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generate Data")
        self.btn_input = QPushButton("Input Data")
        top_layout.addWidget(self.btn_generate)
        top_layout.addWidget(self.btn_input)

        self.btn_cancel = QPushButton("Cancel")
        layout.addLayout(top_layout)
        layout.addWidget(self.btn_cancel)

        self.setLayout(layout)

        # Connect
        self.btn_generate.clicked.connect(self.handle_generate)
        self.btn_input.clicked.connect(self.handle_input)
        self.btn_cancel.clicked.connect(self.close)

    def handle_generate(self):
        all_models = load_all_specialization_models()
        all_features = union_all_features(all_models)
        student_profile = generate_dummy_student(all_features)

        self.hide()
        self.input_window = InputWindow(self.username, student_profile)
        result = self.input_window.exec()
        if result == QDialog.DialogCode.Accepted:
            self.file_path = self.input_window.file_path
            self.accept()  
        else:
            self.reject()
        self.close()


    def handle_input(self):
        # Open empty table for manual input
        self.hide()
        self.input_window = InputWindow(self.username, None)
        result = self.input_window.exec()
        if result == QDialog.DialogCode.Accepted:
            self.file_path = self.input_window.file_path
        self.close()


class InputWindow(QDialog):
    def __init__(self, username, generated_profile=None):
        super().__init__()
        self.generated_profile = generated_profile
        self.username = username
        self.file_path = None
        self.setWindowTitle("Manual Input Window")
        self.setGeometry(250, 250, 600, 500)
        self.init_ui()
        self.populate_table()

    def init_ui(self):
        layout = QVBoxLayout()

        # Table
        self.table = QTableView()
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Code", "Name", "Grade"])
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch)

        self.table.setStyleSheet("""
            QTableView {
                color: black;
                background-color: white;
                border: 2px solid;
                border-radius: 20px;
                border-color: qconicalgradient(cx:0, cy:0.994318, angle:132.9,
                                               stop:0.611111 rgba(16, 0, 66, 255),
                                               stop:1 rgba(91, 48, 255, 255));
                selection-background-color: gray;
            }
        """)

        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)

        # Grade input with validator
        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("Enter grade 0-100")
        validator = QIntValidator(0, 100)
        self.grade_input.setValidator(validator)
        self.grade_input.textChanged.connect(self.update_selected_row_grade)

        # Buttons
        button_layout = QHBoxLayout()
        self.accept_btn = QPushButton("Accept")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.cancel_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.table)
        layout.addWidget(self.grade_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Connect
        self.cancel_btn.clicked.connect(self.reject)
        self.accept_btn.clicked.connect(self.accept_action)

    def populate_table(self):
        """Fill table with either generated data or empty fields."""
        all_models = load_all_specialization_models()
        all_features = union_all_features(all_models)
        self.model.setRowCount(0)

        for feat in all_features:
            item_code = QStandardItem(feat)
            item_name = QStandardItem(feat)
            grade_value = ""

            if self.generated_profile and feat in self.generated_profile:
                grade_value = str(int(self.generated_profile[feat] * 100))

            item_grade = QStandardItem(grade_value)
            item_code.setEditable(False)
            item_name.setEditable(False)
            self.model.appendRow([item_code, item_name, item_grade])

    def update_selected_row_grade(self, text):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            item = QStandardItem(text)
            self.model.setItem(row, 2, item)

    def collect_student_profile(self):
        student_profile = {}
        for row in range(self.model.rowCount()):
            code = self.model.item(row, 0).text()
            grade_item = self.model.item(row, 2)
            if grade_item is None or grade_item.text().strip() == "":
                value = 0.0
            else:
                try:
                    value = float(grade_item.text())
                    if value > 1:
                        value /= 100.0
                except ValueError:
                    value = 0.0
            student_profile[code] = value
        return student_profile

    def accept_action(self):
        """Save prediction and clear grades after confirmation."""
        all_models = load_all_specialization_models()
        if not all_models:
            self.status_label.setText("[ERROR] No models loaded.")
            return
        
        student_profile = self.collect_student_profile()
        df_results = predict_all_compatibilities(all_models, student_profile)
        self.file_path = save_results(df_results, self.username)

        # Update status and clear grades
        self.status_label.setText("Accepted!")
        for row in range(self.model.rowCount()):
            self.model.setItem(row, 2, QStandardItem(""))

        self.accept()

def input_window(username):
    """Open the Input GUI window and wait until the user finishes.

    Returns:
        str | None: The file path of the generated Excel file,
                    or None if the user canceled or closed the dialog.
    """
    global _window_ref

    # Reuse existing QApplication if already running
    app = QApplication.instance()
    own_app = False
    if app is None:
        app = QApplication(sys.argv)
        own_app = True

    # Create and open the intro dialog
    intro = IntroWindow(username)
    _window_ref = intro

    # Run as a blocking dialog (waits until user closes)
    result = intro.exec()

    # If accepted, return file path; else None
    if result == QDialog.DialogCode.Accepted:
        return getattr(intro, "file_path", None)
    else:
        return None

    # If no external app existed, quit it
    if own_app:
        app.quit()
