import sys
from PyQt6.QtWidgets import QApplication
from gui.interface import DataScan

def main():
    app = QApplication(sys.argv)
    window = DataScan()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()