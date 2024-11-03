from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox, QWidget

from gui.style.icon import ICONS
from gui.style.theme import NAV_LABEL_STYLE
from gui.tab.base_tab import BaseTab


class SpaceTimeSelectTab(BaseTab):
    def __init__(self, parent=None):
        name = {
            'en': 'space_time_select',
            'zh': '通道与时间',
        }
        icon = ICONS.qta(name='mdi6.text-search-variant')
        super().__init__(name, icon, parent)

        self.__adjust_ui()
        self.__setup_slot()
        self.setLayout(self.lay)

    def __adjust_ui(self):
        self.lay_time = QGridLayout()
        self.widget_time = QWidget()

        self.title.setText('选择通道与时间范围')
        self.label_time_len = QLabel('时间窗')
        self.desc_time_len = QLabel('4 分钟')
        self.cnt_time_len = QLabel('共 150 个')
        self.label_time_start = QLabel(' 起始')
        self.label_time_end = QLabel(' 终止')
        self.spin_time_start = QSpinBox()
        self.spin_time_end = QSpinBox()

        self.spin_time_start.setRange(1, 1)
        self.spin_time_start.stepBy(1)
        self.spin_time_end.setRange(1, 1)
        self.spin_time_end.stepBy(1)

        self.label_time_len.setStyleSheet(NAV_LABEL_STYLE)
        self.desc_time_len.setStyleSheet(NAV_LABEL_STYLE)
        self.cnt_time_len.setStyleSheet(NAV_LABEL_STYLE)

        self.lay_time.addWidget(self.label_time_len, 0, 0, 1, 1)
        self.lay_time.addWidget(self.desc_time_len, 0, 1, 1, 1)
        self.lay_time.addWidget(self.cnt_time_len, 0, 2, 1, 1)
        self.lay_time.addWidget(self.label_time_start, 1, 0, 1, 1)
        self.lay_time.addWidget(self.spin_time_start, 1, 1, 1, 2)
        self.lay_time.addWidget(self.label_time_end, 2, 0, 1, 1)
        self.lay_time.addWidget(self.spin_time_end, 2, 1, 1, 2)
        self.widget_time.setLayout(self.lay_time)

        self.lay.addWidget(self.widget_time)

    def __setup_slot(self):
        self.btn_affirm.clicked.connect(self.on_affirm_btn_clicked)

    def collect_time_range(self):
        return self.spin_time_start.value(), self.spin_time_end.value()

    @Slot(list, int, int)
    def on_read_out_file_meta(self, ch_list: list[str], wnd_cnt: int, wnd_len: int):
        mins = round(wnd_len / 60, 2)
        self.label_time_len.setText(f'时间窗')
        self.desc_time_len.setText(f'{str(mins)} 分钟')
        self.cnt_time_len.setText(f'共 {str(wnd_cnt)} 个')
        self.spin_time_start.setRange(1, wnd_cnt)
        self.spin_time_end.setRange(1, wnd_cnt)
        self.spin_time_end.setValue(wnd_cnt)

        pairs = {}
        for (idx, ch) in enumerate(ch_list):
            pairs.update({ch: idx})
        self.replace_list_items(pairs)

    @Slot()
    def on_affirm_btn_clicked(self):
        pass
