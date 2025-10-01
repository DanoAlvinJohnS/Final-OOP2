from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPixmap, QPalette
from animations import FancyCircularProgress


class login_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("login.ui", self)

        image_path = "C:/Users/TIPQC/Videos/OOPIntro_Dano/Final-OOP2/sources/Picture1.png"
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        pallette = QPalette()

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("dashboard.ui", self)

        # hook list to stacked widget
        self.listWidget.currentRowChanged.connect(self.mainStackWig.setCurrentIndex)
        self.listWidget.setCurrentRow(0)

        # Create circular progress widgets
        self.g1 = FancyCircularProgress()
        self.g2 = FancyCircularProgress()
        self.g3 = FancyCircularProgress()
        self.g4 = FancyCircularProgress()

        # fix size so they stay circular
        for g in (self.g1, self.g2, self.g3, self.g4):
            g.setFixedSize(200, 200)

        # put them into processGrid
        self.progressGrid.addWidget(self.g1, 0, 0)
        self.progressGrid.addWidget(self.g2, 0, 1)
        self.progressGrid.addWidget(self.g3, 1, 0)
        self.progressGrid.addWidget(self.g4, 1, 1)

        # when page changes, check if it's "statistic"
        self.mainStackWig.currentChanged.connect(self._on_page_changed)

    def _on_page_changed(self, index: int):
        if self.mainStackWig.widget(index) is self.statistic:
            self.g1.setTargetValue(25)
            self.g2.setTargetValue(50)
            self.g3.setTargetValue(75)
            self.g4.setTargetValue(90)
        else:
            self.g1.setTargetValue(0)
            self.g2.setTargetValue(0)
            self.g3.setTargetValue(0)
            self.g4.setTargetValue(0)
                  
    
    

    