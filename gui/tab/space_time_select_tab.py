from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox


from gui.style.icon import ICONS
from gui.tab.base_tab import BaseTab


class SpaceTimeSelectTab(BaseTab):
    def __init__(self, parent=None):
        name = {
            'en': 'space_time_select',
            'zh': '通道与时间',
        }
        icon = ICONS.qta(name='mdi6.text-search-variant')
        super().__init__(name, icon, parent)

    def __adjust_ui(self):
        self.lay_time = QGridLayout(parent=self)

        self.title.setText('选择通道与时间范围')
        self.time_len_desc = QLabel('时间窗(4分钟)')
        self.label_time_start = QLabel('起始')
        self.label_time_end = QLabel('终止')
        self.spin_time_start = QSpinBox()
        self.spin_time_end = QSpinBox()

        self.spin_time_start.setRange(1, 1)
        self.spin_time_start.stepBy(1)
        self.spin_time_end.setRange(1, 1)
        self.spin_time_end.stepBy(1)

        self.lay_time.addWidget(self.time_len_desc, 0, 0, 1, 3)
        self.lay_time.addWidget(self.label_time_start, 1, 0, 1, 1)
        self.lay_time.addWidget(self.spin_time_start, 1, 1, 1, 2)
        self.lay_time.addWidget(self.label_time_end, 2, 0, 1, 1)
        self.lay_time.addWidget(self.spin_time_end, 2, 1, 1, 2)

        self.lay.addLayout(self.lay_time)

    def __setup_slot(self):
        self.btn_affirm.clicked.connect(self.on_affirm_btn_clicked)

    def collect_time_range(self):
        return self.spin_time_start.value(), self.spin_time_end.value()

    @Slot(list, int, int)
    def on_read_out_file_meta(self, ch_list: list[str], wnd_cnt: int, wnd_len: int):
        mins = round(wnd_len / 60, 2)
        self.time_len_desc.setText(f'时间窗({str(mins)}分钟)')
        self.spin_time_start.setRange(1, wnd_cnt)
        self.spin_time_end.setRange(1, wnd_cnt)

        pairs = {}
        for (idx, ch) in enumerate(ch_list):
            pairs.update({'ch': idx})
        self.replace_list_items(pairs)

    @Slot()
    def on_affirm_btn_clicked(self):
        pass
