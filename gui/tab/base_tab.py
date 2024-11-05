from abc import abstractmethod

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QGridLayout, \
    QListWidgetItem, QSizePolicy

from gui.style.theme import NAV_LABEL_STYLE, LISTVIEW_INDICATOR_STYLE


class BaseTab(QWidget):
    def __init__(self, name=None, icon=None, parent=None):
        super().__init__(parent=parent)

        self.name = name
        self.custom_icon: QIcon = icon
        self.setObjectName(f"{name['en']}_tab" if name is not None else "base_tab")
        self.__setup_ui()

    def __setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lay = QVBoxLayout()

        self.widget_title = QWidget()
        self.lay_title = QGridLayout()
        self.widget_list = QWidget()
        self.lay_list = QVBoxLayout()

        self.title = QLabel('标题')
        self.title.setStyleSheet(NAV_LABEL_STYLE)
        self.btn_affirm = QPushButton('确认')

        self.lay_title.addWidget(self.title, 0, 0, 1, 2)
        self.lay_title.addWidget(self.btn_affirm, 0, 2, 1, 1)
        self.widget_title.setLayout(self.lay_title)

        self.list_option = QListWidget()
        self.list_option.setStyleSheet(LISTVIEW_INDICATOR_STYLE)
        self.lay_list.addWidget(self.list_option)
        self.widget_list.setLayout(self.lay_list)

        self.lay.addWidget(self.widget_title)
        self.lay.addWidget(self.widget_list)

    @abstractmethod
    def __adjust_ui(self):
        pass

    @abstractmethod
    def __setup_slot(self):
        pass

    def add_list_item(self, text, data):
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, data)
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemNeverHasChildren |
            Qt.ItemFlag.ItemIsDragEnabled
        )
        item.setCheckState(Qt.CheckState.Unchecked)
        self.list_option.addItem(item)

    def clear_list_item(self):
        self.list_option.clear()

    def replace_list_items(self, pairs: dict[str, object]):
        self.clear_list_item()
        for (key, val) in pairs.items():
            self.add_list_item(key, val)

    def collect_checked_items(self):
        items = {}
        n_items = self.list_option.count()
        for i in range(n_items):
            item = self.list_option.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                items.update({item.text(): item.data(Qt.ItemDataRole.UserRole)})
        return items




