from PySide6.QtCore import Slot


from gui.style.icon import ICONS
from gui.tab.base_tab import BaseTab


class SubjectSelectTab(BaseTab):
    def __init__(self, parent=None):
        name = {
            'en': 'subject_select',
            'zh': '个体选择',
        }
        icon = ICONS.qta(name='mdi6.database-plus-outline')
        super().__init__(name, icon, parent)

    def __adjust_ui(self):
        self.title.setText('选择需分析的个体')

    def __setup_slot(self):
        self.btn_affirm.clicked.connect(self.on_affirm_btn_clicked)

    @Slot()
    def on_affirm_btn_clicked(self):
        pass



