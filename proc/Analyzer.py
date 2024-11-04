import os

from PySide6.QtCore import QObject, Slot, Signal
from sonpy import lib as sp
from sonpy.amd64.sonpy import SonFile

from utils.log import LOG
from utils.path import data_src_dir, data_tgt_dir, epoch_file_ext_name, raw_eeg_file_ext_name


class Analyzer(QObject):
    sig_raw_extract_done = Signal()
    sig_extract_error = Signal(str)
    sig_psd_calc_plot_done = Signal()

    def __init__(self):
        super().__init__()
        self.sec_wnd = 4
        self.fs = -1
        self.sub_pairs = {}
        self.ch_pairs = {}
        self.time_range: tuple[int, int] = (0, 0)

    def reset(self):
        pass

    @Slot(dict)
    def rev_sub_selection(self, pairs):
        self.sub_pairs = pairs




    @Slot(dict, tuple)
    def rev_ch_time_selection(self, pairs, t_range):
        self.ch_pairs = pairs
        self.time_range = t_range

    def collect_raw_meta(self, pair: dict):
        src_dir = data_src_dir()
        tgt_dir = data_tgt_dir()

        ch_pair_list = []

        for k in pair.keys():
            sub_src = os.path.join(src_dir, k+raw_eeg_file_ext_name())
            handle = sp.SonFile(sub_src, True)
            if handle.GetOpenError() != 0:
                raise RuntimeError(
                    f'无法打开文件 {sub_src}，原因: {sp.GetErrorString(handle.GetOpenError())}'
                )

    def read_sonpy_meta_info(self, handle: SonFile):
        ch_pair = {}
        file_ch_meta = []
        n_ch = handle.MaxChannels()
        for ch in range(n_ch):
            if handle.ChannelType(ch) == sp.DataType.Adc:
                fs = round(1 / handle.GetTimeBase())
                if self.fs < 0:
                    self.fs = fs
                else:
                    if self.fs != round(1 / handle.GetTimeBase()):
                        raise RuntimeError(
                            f'两份样本采样频率不同，基准值 {self.fs}，异常值 {}'
                        )


    def extract_raw_pts(self):
        pass

    def send_meta_to_space_time_tab(self):
        pass

    def calc_band_psd(self):
        pass


    def rearrange_intermediate_data(self):
        pass

    def calc_and_save_plot(self):
        pass