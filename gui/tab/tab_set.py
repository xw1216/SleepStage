from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTabWidget, QSizePolicy

from gui.tab.space_time_select_tab import SpaceTimeSelectTab
from gui.tab.subject_select_tab import SubjectSelectTab


class TabSetWidget(QTabWidget):
    tab_list = [
        SubjectSelectTab,
        SpaceTimeSelectTab
    ]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tabs = []

        self.__setup_ui()

    def __setup_ui(self):
        self.setTabPosition(self.TabPosition.North)
        self.setTabShape(self.TabShape.Rounded)

        for tab_func in self.tab_list:
            tab = tab_func(parent=self)
            self.addTab(tab, tab.name['zh'])
            self.tabs.append(tab)

        self.setCurrentIndex(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @Slot(dict)
    def on_subject_select_complete(self, items):
        pass

    @Slot(dict, tuple)
    def on_space_time_select_complete(self, items, t_range):
        pass


