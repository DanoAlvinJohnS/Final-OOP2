# ui_styles_flashcard.py
from PyQt6.QtGui import QFont

APP_STYLE = """
QWidget {
    background-color: #FFF5E5;
}
QPushButton {
    background-color: #FC483D;
    color: white;
    font-size: 33px;
    font-weight: 900;
    border-radius: 30px;
    padding: 14px 40px;
}
QPushButton:hover {
    background-color: #434190;
}
QLineEdit {
    padding: 10px;
    font-size: 18px;
    border-radius: 8px;
    border: 2px solid #CBD5E0;
    background-color: #fefefe;   
    color: #000000;
}
"""

SIDEBAR_BUTTON_STYLE = """
QPushButton {
    background:none;
    color:white;
    text-align:left;
    padding:10px;
    font-size:16px;
    border:none;
}
QPushButton:hover {
    background-color: #434190;
}
"""

HAMBURGER_STYLE = """
QPushButton {
    font-size:24px;
    background:none;
    border:none;
    color:#FC483D;
    padding:10px;
}
QPushButton:hover {
    color:#434190;
}
"""

APP_STYLE_LIGHT = """
QWidget {
    background-color: #FFF5E5;
    color: #2d3436;
}
QPushButton {
    background-color: #FC483D;
    color: white;
    font-size: 16px;
    border-radius: 10px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #e6392d;
}
"""

APP_STYLE_DARK = """
QWidget {
    background-color: #1e1e1e;
    color: #f5f5f5;
}
QPushButton {
    background-color: #3a3a3a;
    color: white;
    font-size: 16px;
    border-radius: 10px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #505050;
}
"""

CREATE_FLASH = """
QWidget {
    background-color: #FC483D;
}
QPushButton {
    background-color: #FC483D;
    color: #FFF5E5;
    font-size: 33px;
    font-weight: 900;
    border-radius: 30px;
    padding: 14px 40px;
}
QPushButton:hover {
    background-color: #434190;
}
"""

MESSAGE_WARNING = """
QMessageBox {
    background-color: #FFF5E5;
    font-size: 16px;
}
QLabel {
    color: #FC483D
}
QPushButton {
    background-color: #FC483D;
    color: #FFF5E5;
    padding: 6px 18px;
    border-radius: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #434190;
}
"""


FONT_SUBTITLE = QFont("Rubik Mono", 16, QFont.Weight.Bold)
FONT_LARGE_BOLD = QFont("Rubik Mono", 28, QFont.Weight.Bold)
FONT_MEDIUM = QFont("Rubik Mono", 26, QFont.Weight.Medium)
FONT_BUTTON = QFont("Rubik Mono", 18)
FONT_LABEL = QFont("Rubik Mono", 24, QFont.Weight.Bold)