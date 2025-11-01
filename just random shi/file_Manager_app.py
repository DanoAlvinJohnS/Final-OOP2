
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QTextEdit, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QStatusBar
)

from PyQt6.QtCore import QTimer
import sys, os

class FileManagerApp(QMainWindow): 
    def __init__(self): 
        super().__init__()
        self.setWindowTitle("File Manager App") 
        self.setFixedSize(600, 500)
        
        # Widgets
        self.title_label = QLabel("Simple File Manager")
        self.text_area = QTextEdit()
        self.load_button = QPushButton("Load File") 
        self.save_button = QPushButton("Save File")
        self.append_button = QPushButton("Append Text")
        self.clear_button = QPushButton("Clear Text")
        
        #Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar) 
        self.status_bar.showMessage("Ready")
      
        #Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.append_button) 
        button_layout.addWidget(self.clear_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label) 
        main_layout.addWidget(self.text_area)
        main_layout.addLayout(button_layout)
        
        container = QWidget()
        container.setLayout(main_layout) 
        self.setCentralWidget(container)
      
        #Signal Collection
        self.load_button.clicked.connect(self.load_file)
        self.save_button.clicked.connect(self.save_file)
        self.append_button.clicked.connect(self.append_text)
       # self.clear_button.clicked.connect(self.clear_text)

    def load_file(self):
        try:
            path, _  = QFileDialog.getOpenFileName(self, "Open File", "Text Files (*.txt)")
            if path and os.path.exists(path):
                with open(path, "r") as file: 
                    content = file.read()
                self.text_area.setPlainText(content)
                self.status_bar.showMessage(f"Loaded: {os.path.basename(path)}")
            else:
                self.status_bar.showMessage("No file selected.")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot load file:\n{e}")

    def save_file(self):
        try:
            path, _=  QFileDialog.getSaveFileName(self, "Save File", "Text Files (*.txt)")
            if path: 
                with open(path, "w") as file:
                    file.write(self.text_area.toPlainText())
                self.status_bar.showMessage(f"File saved at: {path}")
                QMessageBox.information(self, "Success", "File saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed:\n{e}")

    def append_text(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Append to File", "Text Files (*.txt)")
            if path:
                with open(path, "a") as file:
                    file.write("\n" + self.text_area.toPlainText())
                QMessageBox.information(self, "Appended", "Content successfully appended!") 
                self.status_bar.showMessage("Text appended successfully.")

        except Exception as e:
                QMessageBox.warning(self, "Error", f"Append failed:\n{e}")

    def clear_text(self):   
        self.text_area.clear()
        self.status_bar.showMessage("[OK] | Text area cleared.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManagerApp()
    window.show()  
    sys.exit(app.exec())     
    