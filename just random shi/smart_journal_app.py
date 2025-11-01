
from PyQt6.QtWidgets import QApplication
from smart_journey_handler import Manager
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Manager()
    window.show()  
    sys.exit(app.exec())     
    