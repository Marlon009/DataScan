import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from gui.interface import DataScan as MainWindow

def main():
    app = QApplication(sys.argv)

    # Carregar imagem do splash
    splash_pix = QPixmap("datascanimg.png").scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    # Após 3 segundos, exibe a janela principal
    def show_main():
        window = MainWindow()
        window.show()
        splash.finish(window)

    QTimer.singleShot(2000, show_main)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()