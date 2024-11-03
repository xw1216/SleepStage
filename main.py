import sys
import ctypes

import pyqtgraph
from PySide6 import QtWidgets
from qt_material import apply_stylesheet

from gui.home import MainGUI
from gui.style.theme import *


if __name__ == "__main__":
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MiceSleepAnalysis")

    theme = 'light_blue_500.xml'
    app = QtWidgets.QApplication([])
    apply_stylesheet(
        app,
        theme,
        invert_secondary=('light' in theme and 'dark' not in theme),
        extra=THEME_EXTRA
    )
    pyqtgraph.setConfigOption('background', 'w')

    widget = MainGUI()
    widget.show()
    sys.exit(app.exec())
