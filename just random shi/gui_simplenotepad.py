import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGroupBox, QTextEdit, QPushButton,
    QAction, QFileDialog, QFontDialog
)
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notepad")
        self.setWindowIcon(QIcon("pythonico.ico"))

        self.notepad = Notepad()
        self.setCentralWidget(self.notepad)

        self.loadMenu()
        self.show()

    def loadMenu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        editMenu = mainMenu.addMenu("Edit")

        openButton = QAction("Open", self)
        openButton.setShortcut("Ctrl+O")
        openButton.triggered.connect(self.openFileDialog)
        fileMenu.addAction(openButton)

        saveButton = QAction("Save", self)
        saveButton.setShortcut("Ctrl+S")
        saveButton.triggered.connect(self.saveFileDialog)
        fileMenu.addAction(saveButton)

        exitButton = QAction("Exit", self)
        exitButton.setShortcut("Ctrl+Q")
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        clearButton = QAction("Clear", self)
        clearButton.setShortcut("Ctrl+M")
        clearButton.triggered.connect(self.clearText)
        editMenu.addAction(clearButton)

        fontButton = QAction("Font", self)
        fontButton.setShortcut("Ctrl+D")
        fontButton.triggered.connect(self.showFontDialog)
        editMenu.addAction(fontButton)

    def saveFileDialog(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Notepad File", "",
            "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )
        if fileName:
            with open(fileName, "w", encoding="utf-8") as file:
                file.write(self.notepad.text.toPlainText())

    def openFileDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Notepad File", "",
            "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )
        if fileName:
            with open(fileName, "r", encoding="utf-8") as file:
                data = file.read()
                self.notepad.text.setPlainText(data)

    def clearText(self):
        self.notepad.text.clear()

    def showFontDialog(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.notepad.text.setFont(font)

class Notepad(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QTextEdit(self)

        self.initUI()

    def initUI(self):
        self.horizontalGroupBox = QGroupBox("Notepad Area")
        layout = QHBoxLayout()
        layout.addWidget(self.text)
        self.horizontalGroupBox.setLayout(layout)

        # Main window layout
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
