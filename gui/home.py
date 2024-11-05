import logging

from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QStatusBar
from qt_material import QtStyleTools

from gui.tab.tab_set import TabSetWidget
from proc.analyzer import Analyzer
from utils.log import LOG


class MainGUI(QMainWindow, QtStyleTools):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MiceSleepAnalysis')
        self.kit = Analyzer()

        self.__setup_ui()
        self.__setup_slot()
        self.auto_resize()
        self.move_center()

    def __setup_ui(self):
        self.statusbar = QStatusBar(self)
        self.tab_set = TabSetWidget(self.kit, self)

        self.setStatusBar(self.statusbar)
        LOG.register_status_bar(self.statusbar)
        self.statusbar.showMessage('状态栏')

        self.setCentralWidget(self.tab_set)

    def __setup_slot(self):
        pass

    def auto_resize(self):
        screen = QGuiApplication.primaryScreen().geometry()
        width = screen.width() // 4
        height = screen.height() // 2
        size = QSize(width, height)
        self.setMinimumSize(size)
        self.resize(size)

    def move_center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()
        cen_x = (screen.width() - size.width()) // 2
        cen_y = (screen.height() - size.height()) // 2
        self.move(cen_x, cen_y)