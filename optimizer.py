import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    Application entry point.
    """
    app = QApplication(sys.argv)
    
    # Standard high-DPI scaling for modern displays
    app.setApplicationName("OptiVidio")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
