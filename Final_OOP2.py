from PyQt6.QtWidgets import QApplication
from start_up import CareerExplorer
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CareerExplorer()
    window.show()  
    sys.exit(app.exec())