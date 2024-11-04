from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox, QWidget, QScrollBar, QSlider, QMessageBox

from gui.style.icon import ICONS
from gui.style.theme import NAV_LABEL_STYLE
from gui.tab.base_tab import BaseTab
from utils.log import LOG


class SpaceTimeSelectTab(BaseTab):
    sig_space_time_sel_done = Signal(dict, tuple)
    def __init__(self, parent=None):
        name = {
            'en': 'space_time_select',
            'zh': '通道与时间',
        }
        icon = ICONS.qta(
            'mdi6.magnify-scan',
            options=[
                {'color': QColor.fromString('#000000')}
            ]
        )
        super().__init__(name, icon, parent)
        self.wnd_sec = 4
        self.wnd_cnt = 500

        self.__adjust_ui()
        self.__setup_slot()
        self.setLayout(self.lay)

    def __adjust_ui(self):
        self.lay_time = QGridLayout()
        self.widget_time = QWidget()

        self.title.setText('选择通道与时间范围')
        self.label_time_len = QLabel('时间窗')
        self.desc_time_len = QLabel('每个 4 秒种')
        self.cnt_time_len = QLabel('共 150 个')
        self.label_time_start = QLabel(' 起始')
        self.label_time_start_convert = QLabel('0 小时 0 分钟 0 秒')
        self.label_time_end = QLabel(' 终止')
        self.label_time_end_convert = QLabel('0 小时 0 分钟 0 秒')
        self.bar_time_start = QSlider(orientation=Qt.Orientation.Horizontal)
        self.bar_time_end = QSlider(orientation=Qt.Orientation.Horizontal)

        self.desc_time_len.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_time_start_convert.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_time_end_convert.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bar_time_start.setSingleStep(1)
        self.bar_time_start.setPageStep(15)
        self.bar_time_end.setSingleStep(1)
        self.bar_time_end.setPageStep(15)

        self.label_time_len.setStyleSheet(NAV_LABEL_STYLE)
        self.desc_time_len.setStyleSheet(NAV_LABEL_STYLE)
        self.cnt_time_len.setStyleSheet(NAV_LABEL_STYLE)

        self.lay_time.addWidget(self.label_time_len, 0, 0, 1, 1)
        self.lay_time.addWidget(self.cnt_time_len, 0, 1, 1, 2)
        self.lay_time.addWidget(self.desc_time_len, 0, 3, 1, 2)
        self.lay_time.addWidget(self.label_time_start, 1, 0, 1, 1)
        self.lay_time.addWidget(self.bar_time_start, 1, 1, 1, 2)
        self.lay_time.addWidget(self.label_time_start_convert, 1, 3, 1, 2)
        self.lay_time.addWidget(self.label_time_end, 2, 0, 1, 1)
        self.lay_time.addWidget(self.bar_time_end, 2, 1, 1, 2)
        self.lay_time.addWidget(self.label_time_end_convert, 2, 3, 1, 2)
        self.widget_time.setLayout(self.lay_time)

        self.lay.addWidget(self.widget_time)

    def __setup_slot(self):
        self.btn_affirm.clicked.connect(self.on_affirm_btn_clicked)
        self.bar_time_start.valueChanged[int].connect(self.on_start_slider_change)
        self.bar_time_end.valueChanged[int].connect(self.on_end_slider_change)

    def collect_time_range(self):
        return self.bar_time_start.value() - 1, self.bar_time_end.value()

    @Slot(list, int, int)
    def on_read_out_file_meta(self, ch_list: list[str], wnd_cnt: int, wnd_sec: int):
        self.wnd_cnt = wnd_cnt
        self.wnd_sec = wnd_sec

        self.desc_time_len.setText(f'每个 {str(wnd_sec)} 秒钟')
        self.cnt_time_len.setText(f'共 {str(self.wnd_cnt)} 个')

        self.bar_time_start.setRange(1, self.wnd_cnt)
        self.bar_time_end.setRange(1, self.wnd_cnt)
        self.bar_time_start.setValue(1)
        self.bar_time_end.setValue(wnd_cnt)

        pairs = {}
        for (idx, ch) in enumerate(ch_list):
            pairs.update({ch: idx})
        self.replace_list_items(pairs)

    @Slot(int)
    def on_start_slider_change(self, val):
        val -= 1
        s = self.time_format_converter(val)
        self.label_time_start_convert.setText(s)

    @Slot(int)
    def on_end_slider_change(self, val):
        s = self.time_format_converter(val)
        self.label_time_end_convert.setText(s)

    def time_format_converter(self, cnt: int):
        secs_total = cnt * self.wnd_sec
        hours = secs_total // 3600
        mins = (secs_total - hours * 3600) // 60
        secs = (secs_total - hours * 3600 - mins * 60)
        return f'{hours} 小时 {mins} 分钟 {secs} 秒'

    @Slot()
    def on_affirm_btn_clicked(self):
        items = self.collect_checked_items()
        t_range = self.collect_time_range()

        if len(items) == 0:
            QMessageBox.warning(self, "警告", "没有选择任何通道")
            return
        elif t_range[0] > t_range[1]:
            QMessageBox.warning(self, "警告", "起始时间不能大于终止时间")
            return

        self.sig_space_time_sel_done.emit(items, t_range)
        LOG.info('通道与时间选择完成')
