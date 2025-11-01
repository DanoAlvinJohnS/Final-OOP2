from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QScrollArea, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt
from ui_handler.animations import FancyCircularProgress

class login_window(QWidget):
    def __init__(self, parent=None, status=None):
        super().__init__(parent)
        self.status = status  

        if self.status == "login":
            uic.loadUi("ui/login.ui", self)
        elif self.status == "register":
            uic.loadUi("ui/register.ui", self)

class DashboardWidget(QWidget):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.username = username

        uic.loadUi("ui/dashboard.ui", self)
        self.load_data(username)

        # connect sidebar to stacked widget
        self.listWidget.currentRowChanged.connect(self.mainStackWig.setCurrentIndex)
        self.listWidget.setCurrentRow(0)

        # listen for page changes
        self.mainStackWig.currentChanged.connect(self._on_page_changed)

    def _on_page_changed(self, index: int):
        """Animate progress only when statistic page is shown."""
        current_page = self.mainStackWig.widget(index)

        if current_page is self.statistic:
            # Create statistic page once (lazy loading)
            if not hasattr(self, "g1"):
                self._create_statistic_page()

            # Animate progress
            self.g1.setTargetValue(25)
            self.g2.setTargetValue(50)
            self.g3.setTargetValue(75)
            self.g4.setTargetValue(90)
        else:
            # Reset values when leaving the page
            if hasattr(self, "g1"):
                for g in (self.g1, self.g2, self.g3, self.g4):
                    g.setTargetValue(0)

    def load_data(self, username):
        if hasattr(self, "user_name"):
            self.user_name.setText(f"{username}")
        else:
            print("Developer || QLabel 'user_name' not found in dashboard.ui")
