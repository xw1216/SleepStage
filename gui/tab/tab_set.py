from PySide6.QtCore import Slot, QSize, SIGNAL, Signal
from PySide6.QtWidgets import QTabWidget, QSizePolicy, QMessageBox, QFileDialog

from gui.tab.base_tab import BaseTab
from gui.tab.space_time_select_tab import SpaceTimeSelectTab
from gui.tab.subject_select_tab import SubjectSelectTab
from proc.analyzer import Analyzer
from utils.log import LOG


class TabSetWidget(QTabWidget):
    tab_list = [
        SubjectSelectTab,
        SpaceTimeSelectTab
    ]

    sig_start_raw_extract = Signal(dict)
    sig_start_psd_plot = Signal(dict, tuple, str)
    sig_read_out_file_meta = Signal(list[str], int, int)

    def __init__(self, kit=None, parent=None):
        super().__init__(parent=parent)
        self.tabs: list[BaseTab] = []
        self.kit: Analyzer = kit

        self.__setup_ui()
        self.__setup_slot()

    def __setup_ui(self):
        self.setTabPosition(self.TabPosition.North)
        self.setTabShape(self.TabShape.Rounded)
        self.setIconSize(QSize(22, 22))

        for (idx, tab_func) in enumerate(self.tab_list):
            tab = tab_func(parent=self)
            if isinstance(tab, SpaceTimeSelectTab):
                tab.on_read_out_file_meta(['EEG-1', 'EEG-2', 'EMG-1'], 500, 4)
            self.addTab(tab, tab.custom_icon, tab.name['zh'])
            self.tabs.append(tab)

        self.setCurrentIndex(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def __setup_slot(self):
        for tab in self.tabs:
            if isinstance(tab, SubjectSelectTab):
                tab.sig_sub_sel_done.connect(self.on_subject_select_done)
                self.sig_start_raw_extract.connect(self.kit.rev_sub_selection)
                self.kit.sig_raw_extract_done.connect(self.on_raw_extract_done)
                self.kit.sig_extract_error.connect(self.on_extract_error)
            elif isinstance(tab, SpaceTimeSelectTab):
                self.sig_read_out_file_meta.connect(tab.on_read_out_file_meta)
                tab.sig_space_time_sel_done.connect(self.on_space_time_select_done)
                self.kit.sig_psd_calc_plot_done.connect(self.on_psd_calc_plot_done)


    @Slot(dict)
    def on_subject_select_done(self, sub_pair: dict):
        LOG.info('完成个体选择，即将提取文件数据')
        self.sig_start_raw_extract.emit(sub_pair)


    @Slot()
    def on_raw_extract_done(self, chs: list[str], wnd_cnt: int, wnd_sec: int):
        self.setCurrentIndex(1)
        self.sig_read_out_file_meta.emit(chs, wnd_cnt, wnd_sec)

    @Slot(str)
    def on_extract_error(self, msg: str):
        QMessageBox.critical(self, '警告', msg)
        LOG.error(msg)
        self.setCurrentIndex(0)

    @Slot(dict, tuple)
    def on_space_time_select_done(self, items, t_range):
        save_path = QFileDialog.getExistingDirectory(caption='请选择结果保存文件夹')
        save_path = str(save_path)
        self.sig_start_psd_plot.emit(items, t_range, save_path)
        LOG.info('开始数据分析')

    @Slot()
    def on_psd_calc_plot_done(self):
        QMessageBox.information(self, '通知', '分析成功完成')
        LOG.info('分析完成')




