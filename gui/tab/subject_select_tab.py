import os.path
from re import escape

from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QMessageBox

from gui.style.icon import ICONS
from gui.tab.base_tab import BaseTab
from utils.log import LOG
from utils.path import epoch_file_ext_name


class SubjectSelectTab(BaseTab):
    sig_scan_done = Signal(list)
    sig_sub_sel_done = Signal(dict)

    def __init__(self, parent=None):
        name = {
            'en': 'subject_select',
            'zh': '个体选择',
        }
        icon = ICONS.qta(
            'mdi6.database-plus-outline',
            options=[
                {'color': QColor.fromString('#000000')}
            ]
        )
        super().__init__(name, icon, parent)

        self.__adjust_ui()
        self.__setup_slot()
        self.setLayout(self.lay)

    def __adjust_ui(self):
        self.lay_sel_btn = QGridLayout()
        self.widget_sel_btn = QWidget()
        self.btn_scan = QPushButton('扫描')

        self.btn_sel_all = QPushButton('全选')
        self.btn_sel_none = QPushButton('全不选')

        self.title.setText('选择需分析的个体')
        self.lay_title.removeWidget(self.btn_affirm)
        self.lay_title.addWidget(self.btn_scan, 0, 2, 1, 1)
        self.lay_title.addWidget(self.btn_affirm, 0, 3, 1, 1)

        self.lay_sel_btn.addWidget(self.btn_sel_all, 0, 0, 1, 1)
        self.lay_sel_btn.addWidget(self.btn_sel_none, 0, 1, 1, 1)

        self.widget_sel_btn.setLayout(self.lay_sel_btn)

        self.lay.addWidget(self.widget_sel_btn)

    def __setup_slot(self):
        self.btn_affirm.clicked.connect(self.on_affirm_btn_clicked)
        self.btn_sel_all.clicked.connect(self.on_sel_all_btn_clicked)
        self.btn_sel_none.clicked.connect(self.on_sel_none_btn_clicked)
        self.btn_scan.clicked.connect(self.on_scan_btn_clicked)
        self.sig_scan_done.connect(self.on_file_scan_done)

    @staticmethod
    def scan_raw_data():
        subjects = []
        src_dir = os.path.join(os.getcwd(), 'dataset', 'raw')
        tgt_dir = os.path.join(os.getcwd(), 'dataset', 'extract')
        os.makedirs(tgt_dir, exist_ok=True)

        files_all = os.listdir(src_dir)
        for f in files_all:
            if len(f.split('.')) != 2:
                continue

            [name, ext] = f.split('.')
            if ext != 'smrx':
                continue

            sub = f.split('_')[0]
            csv_f = name.split('_')[0] + epoch_file_ext_name()
            if csv_f in files_all:
                subjects.append(sub)

        return subjects

    @Slot()
    def on_scan_btn_clicked(self):
        LOG.info('扫描可分析文件中')
        subjects = self.scan_raw_data()
        self.sig_scan_done.emit(subjects)

    @Slot(list)
    def on_file_scan_done(self, subjects: list):
        LOG.info('扫描完成')
        if len(subjects) < 1:
            QMessageBox.warning(self, "通知", "没有可以分析的个体，请检查文件格式是否正确完整")
            LOG.info('没有可分析个体')
            self.clear_list_item()
            return
        else:
            LOG.info(f'共扫描到 {len(subjects)} 个可分析个体')
            LOG.info(f'个体列表 {subjects}', sync=False)
            sub_sets = set(subjects)
            subjects = list(sub_sets)
            if len(sub_sets) != len(subjects):
                QMessageBox.information(self, "通知", "有重名个体，请检查文件命名")
                LOG.info('检测到重名个体')
                return
            subjects.sort()
            pairs = {}
            for (idx, sub) in enumerate(subjects):
                pairs.update({sub: idx})

            self.replace_list_items(pairs)

    @Slot()
    def on_affirm_btn_clicked(self):
        pairs = self.collect_checked_items()
        if len(pairs.keys()) < 1:
            QMessageBox.information(self, "通知",
                                    "没有选择任何个体")
            return
        self.sig_sub_sel_done.emit(pairs)


    @Slot()
    def on_sel_all_btn_clicked(self):
        self.change_list_check_state(True)

    @Slot()
    def on_sel_none_btn_clicked(self):
        self.change_list_check_state(False)

    def change_list_check_state(self, state: bool):
        if not state:
            s = Qt.CheckState.Unchecked
        else:
            s = Qt.CheckState.Checked

        for i in range(self.list_option.count()):
            item = self.list_option.item(i)
            item.setCheckState(s)


