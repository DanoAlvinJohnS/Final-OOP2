from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPixmap, QPalette
from animations import FancyCircularProgress


class login_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("login.ui", self)
        # uic.loadUi("dashboard.ui", self)

        image_path = "C:/Users/TIPQC/Videos/OOPIntro_Dano/Final-OOP2/sources/Picture1.png"
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        pallette = QPalette()

class DashboardWidget(QWidget):    
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("dashboard.ui", self)
                  
    
    

    