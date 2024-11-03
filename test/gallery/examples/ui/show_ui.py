from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from qt_material import apply_stylesheet
import os

########################################################################
class ShowUI(QMainWindow):
    # ----------------------------------------------------------------------
    def __init__(self, loader):
        """"""
        super().__init__()
        self.main = loader.load(r'window.ui', self)
        print('hello')


if __name__ == "__main__":
    loader = QUiLoader()
    app = QApplication()

    print(os.curdir)

    apply_stylesheet(app, theme='dark_cyan.xml')

    frame = ShowUI(loader)
    frame.main.show()

    app.exec()
