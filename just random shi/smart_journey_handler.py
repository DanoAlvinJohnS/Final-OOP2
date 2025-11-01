from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QDialog,
    QTextEdit, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QStatusBar, QLineEdit,
    QApplication
)
from datetime import datetime
import os, sys

class IntroWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Intro")
        self.setGeometry(200, 200, 400, 200)
        self.name = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top layout for name input
        top_layout = QHBoxLayout()
        self.inputname = QLineEdit()
        self.label_name = QLabel("Name: ")
        top_layout.addWidget(self.label_name)
        top_layout.addWidget(self.inputname)

        # Buttons
        self.btn_input = QPushButton("Accept")
        self.btn_cancel = QPushButton("Cancel")

        layout.addLayout(top_layout)
        layout.addWidget(self.btn_input)
        layout.addWidget(self.btn_cancel)
        self.setLayout(layout)

        # Connect buttons
        self.btn_input.clicked.connect(self.approve)
        self.btn_cancel.clicked.connect(self.close)

    def approve(self):
        self.name = self.inputname.text().strip()
        if self.name:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a name before proceeding.")

class Manager(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Smart Journal App - {self.username}")
        self.setFixedSize(600, 500)

        # Track currently opened file (fixed: initialize here)
        self.current_file = None

        # Widgets
        self.title_label = QLabel(f"Welcome, {self.username}")
        self.text_area = QTextEdit()
        self.load_button = QPushButton("Load File")
        self.save_button = QPushButton("Save Entry")
        self.clear_button = QPushButton("Clear Text")

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.text_area)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Signals
        self.load_button.clicked.connect(self.load_file)
        self.save_button.clicked.connect(self.save_entry)
        self.clear_button.clicked.connect(self.clear_text)

    def load_file(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "journals", "Text Files (*.txt)")
            if path and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.text_area.setPlainText(content)
                self.current_file = path
                self.status_bar.showMessage(f"Loaded: {os.path.basename(path)}")
            else:
                self.status_bar.showMessage("No file selected.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot load file:\n{e}")

    def save_entry(self):
        try:
            # Use getattr as extra safety, but current_file is already initialized in __init__
            if getattr(self, "current_file", None):
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.text_area.toPlainText())
                QMessageBox.information(self, "Saved", f"File updated:\n{os.path.basename(self.current_file)}")
                self.status_bar.showMessage(f"Updated: {os.path.basename(self.current_file)}")
            else:
                folder_path = "journals"
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_name = f"{self.username}_journal_{timestamp}.txt"
                full_path = os.path.join(folder_path, file_name)

                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(f"Journal Entry by {self.username}\n")
                    file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write("-" * 50 + "\n")
                    file.write(self.text_area.toPlainText())

                self.current_file = full_path
                QMessageBox.information(self, "Saved", f"New file created:\n{file_name}")
                self.status_bar.showMessage(f"Saved: {file_name}")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed:\n{e}")

    def clear_text(self):
        self.text_area.clear()
        self.status_bar.showMessage("Text area cleared.")

    def new_entry(self):
        self.text_area.clear()
        self.current_file = None
        self.status_bar.showMessage("Started a new entry (unsaved)")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    intro = IntroWindow()
    if intro.exec() == QDialog.DialogCode.Accepted:
        username = intro.name
        window = Manager(username)
        window.show()
        sys.exit(app.exec())
