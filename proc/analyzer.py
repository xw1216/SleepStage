import os
import shutil

import numpy as np
import pandas as pd
import scipy.signal as sig
import matplotlib.pyplot as plt
from PySide6.QtCore import QObject, Slot, Signal
from matplotlib.ticker import FormatStrFormatter
from sonpy import lib as sp
from sonpy.amd64.sonpy import SonFile

from utils.log import LOG
from utils.path import *


class Analyzer(QObject):
    sig_raw_extract_done = Signal(list, int, int)
    sig_extract_error = Signal(str)
    sig_psd_calc_plot_done = Signal()

    def __init__(self):
        super().__init__()
        self.wnd_sec = 4
        self.wnd_cnt = -1

        self.nfft = 4000
        self.fft_freq_down = 2
        self.fft_freq_up = 120
        self.cnt_band = 4
        self.low_cut = 0.3
        self.high_cut = 30

        self.fs = -1
        self.pts = -1

        self.sub_pair: dict[str, int] = {}
        self.ch_pair: dict[str, int] = {}
        self.time_range: tuple[int, int] = (0, 0)

        self.save_path = '.'

    def reset(self):
        self.wnd_sec = 4
        self.wnd_cnt = -1

        self.nfft = 4000
        self.fft_freq_down = 2
        self.fft_freq_up = 120
        self.cnt_band = 4
        self.low_cut = 0.3
        self.high_cut = 30

        self.fs = -1
        self.pts = -1

        self.sub_pair: dict[str, int] = {}
        self.ch_pair: dict[str, int] = {}
        self.time_range: tuple[int, int] = (0, 0)

        self.save_path = '.'

    @Slot(dict)
    def rev_sub_selection(self, sub_pair: dict[str, int]):
        self.reset()
        self.sub_pair = sub_pair
        try:
            ch_pair = self.collect_raw_meta(sub_pair)
            self.extract_raw_pts(sub_pair, ch_pair)
        except RuntimeError as e:
            self.reset()
            self.sig_extract_error.emit(str(e))
            return

        self.wnd_cnt = self.pts // (self.fs * self.wnd_sec)
        self.sig_raw_extract_done.emit(
            list(ch_pair.keys()),
            self.wnd_cnt, self.wnd_sec
        )

    def collect_raw_meta(self, sub_pair: dict[str, int]):
        src_dir = data_src_dir()
        pair_ch_list = []

        for sub in sub_pair.keys():
            sub_src = os.path.join(src_dir, sub + raw_eeg_file_ext_name())
            handle = self.open_sonpy_file(sub_src)

            file_ch_meta = self.read_sonpy_meta_info(handle)
            pair_ch_list.append(file_ch_meta)
            self.save_sub_info(sub, file_ch_meta)

            self.copy_epoch_files(sub)
            LOG.info(f'正在提取 {sub} 的数据元信息')

        # shape [sub, ch] element dict
        ch_pair = self.check_ch_consist(pair_ch_list)
        return ch_pair

    @staticmethod
    def copy_epoch_files(key: str):
        sub_src_epoch = os.path.join(data_src_dir(), key + epoch_file_ext_name())
        sub_tgt_epoch= os.path.join(data_tgt_dir(), key, key + epoch_file_ext_name())
        shutil.copy(str(sub_src_epoch), str(sub_tgt_epoch))

    @staticmethod
    def save_sub_info(key: str, meta: list):
        tgt_dir = data_tgt_dir()
        sub_tgt = os.path.join(tgt_dir, key)
        os.makedirs(sub_tgt, exist_ok=True)

        df = pd.DataFrame(meta)
        sub_info = os.path.join(sub_tgt, key + info_file_ext_name())
        df.to_csv(sub_info, index=False)

    @staticmethod
    def open_sonpy_file(path):
        handle = sp.SonFile(path, True)
        if handle.GetOpenError() != 0:
            raise RuntimeError(
                f'无法打开源文件 {path}，原因: {sp.GetErrorString(handle.GetOpenError())}'
            )
        return handle

    @staticmethod
    def check_ch_consist(ch_pair_list):
        n_sub = len(ch_pair_list)
        n_ch = len(ch_pair_list[0])

        for sub in range(n_sub):
            if len(ch_pair_list[sub]) != n_ch:
                raise RuntimeError(f'发现样本数据通道数量不一致，基准值 {n_ch}, 异常值 {len(ch_pair_list[sub])}')

        ch_pair = {}
        for ch in range(n_ch):
            ch_name = ''
            for sub in range(n_sub):
                if sub == 0:
                    ch_name = ch_pair_list[sub][ch]['name']
                    ch_idx = ch_pair_list[sub][ch]['ch_idx']
                    ch_pair.update({ch_name: ch_idx})
                else:
                    if ch_name != ch_pair_list[sub][ch]['name']:
                        raise RuntimeError(f'发现样本数据通道排序不同')
        return ch_pair

    def read_sonpy_meta_info(self, handle: SonFile):
        file_ch_meta = []
        n_ch = handle.MaxChannels()
        for ch in range(n_ch):
            if (handle.ChannelType(ch) == sp.DataType.Adc and
                    handle.GetChannelTitle(ch).startswith('M')):

                fs = round(1 / handle.GetTimeBase())
                if self.fs < 0:
                    self.fs = fs
                    self.pts = handle.ChannelMaxTime(ch)
                    self.nfft = self.fs * 4
                else:
                    if self.fs != round(1 / handle.GetTimeBase()):
                        raise RuntimeError(
                            f'存在两份样本采样频率不同，基准值 {self.fs} Hz，异常值 {fs} Hz'
                        )

                pts = handle.ChannelMaxTime(ch)
                self.pts = min(self.pts, pts)
                file_ch_meta.append({
                    'name': handle.GetChannelTitle(ch),
                    'ch_idx': ch,
                    'sec_wnd': self.wnd_sec,
                    'fs': self.fs,
                    'pts': pts,
                    'wnd': pts // (self.fs * self.wnd_sec)
                })

        return file_ch_meta

    def extract_raw_pts(self, sub_pair: dict[str, int], ch_pair: dict[str, int]):
        src_dir = data_src_dir()

        for sub in sub_pair.keys():
            sub_src = os.path.join(src_dir, sub + raw_eeg_file_ext_name())
            handle = self.open_sonpy_file(sub_src)

            wave = np.empty(shape=(0, self.pts))
            for (ch_name, ch_idx) in ch_pair.items():
                data: np.ndarray = handle.ReadFloats(ch_idx, self.pts, 0)
                self.check_data_read_result(data, sub_src)
                data = data.reshape(1, self.pts)
                wave = np.concatenate((wave, data), axis=0)
            self.save_sub_data(sub, wave)
            LOG.info(f'正在提取 {sub} 的信号记录')

    @staticmethod
    def save_sub_data(key: str, data: np.ndarray):
        sub_tgt = os.path.join(data_tgt_dir(), key)
        sub_data = os.path.join(sub_tgt, key + extract_eeg_ext_name())
        np.save(sub_data, data)

    def check_data_read_result(self, data, path):
        if len(data) == 1 and data[0] < 0:
            raise RuntimeError(f'读取数据时错误 {path}: {sp.GetErrorString(int(data[0]))}')
        elif len(data) == 0:
            raise RuntimeError('未能读取数据点')
        elif len(data) != self.pts:
            raise RuntimeError(f'数据样本数不一致, 基准值 {self.pts}， 异常值 {len(data)}')

    @Slot(dict, tuple, str)
    def rev_ch_time_selection(self, ch_pairs: dict, t_range: tuple[int, int], save_path: str):
        self.ch_pair = ch_pairs
        self.time_range = t_range

        info_list = self.calc_sleep_type_psd(t_range)
        self.save_psd_table(info_list, save_path)

        result = self.transpose_info_list(info_list)
        plot_data = self.calc_average_plot_data(result)
        self.plot_and_save_psd(plot_data, save_path)

        self.sig_psd_calc_plot_done.emit()

    def calc_sleep_type_psd(self, t_range: tuple[int, int]):
        # info_list shape [sub, type, (f [freq], p[ch, freq])]
        info_list = []
        for (i, sub) in enumerate(self.sub_pair.keys()):
            info_list.append([])
            sub_dir = os.path.join(data_tgt_dir(), sub)
            data_dir = os.path.join(sub_dir, sub + extract_eeg_ext_name())
            label_dir = os.path.join(sub_dir, sub + epoch_file_ext_name())

            data = np.load(data_dir)
            label = pd.read_csv(label_dir)

            ch_sel = list(self.ch_pair.values())
            data = data[ch_sel, t_range[0] * self.fs * self.wnd_sec:t_range[1] * self.fs * self.wnd_sec]
            LOG.info(f'对 {sub} 个体数据滤波')
            data = self.highpass_filter(data)
            # data = self.lowpass_filter(data)
            data = data.reshape(len(self.ch_pair.keys()), -1, self.fs * self.wnd_sec)

            label = (label['class'].values - 1).reshape(-1)
            label = label[t_range[0]:t_range[1]]

            # 将不同类的时间段分离出来
            wake_idx = np.where(label == 0)[0]
            nrem_idx = np.where(label == 1)[0]
            rem_idx = np.where(label == 2)[0]

            LOG.info(f'计算 {sub} 个体数据频谱图')
            # 遍历三种类别的时间段
            for (name, j) in [
                ('wake', wake_idx),
                ('nrem', nrem_idx),
                ('rem', rem_idx)
            ]:
                # 提取时间段
                wave = data[:, j, :]
                # 傅里叶变换后频谱图，其中 nfft 指定了频率点粒度
                f, p = sig.periodogram(wave, self.fs, axis=2, nfft=self.nfft)

                # 选取限定范围内的频率与功率点对
                f = f[0:self.fft_freq_up + 1]
                p = p[:, :, 0:self.fft_freq_up + 1]
                p = p.mean(axis=1)
                info_list[i].append((f, p))

        # info_list shape [sub, type, (f ndarray [freq], p ndarray [ch, freq])]
        return info_list

    def save_psd_table(self, info_list, save_path):
        LOG.info('保存频谱数据表中')
        save_path = os.path.join(save_path, 'table')
        os.makedirs(save_path, exist_ok=True)

        columns = ['个体', '睡眠类型', '通道', '频率点(Hz)', '功率谱密度(uV^2/Hz)']
        for (i, sub) in enumerate(self.sub_pair.keys()):
            df = pd.DataFrame(columns=columns)
            for (j, tp) in enumerate(['wake', 'nrem', 'rem']):
                freq = info_list[i][j][0]
                psd = info_list[i][j][1]
                for (k, ch) in enumerate(self.ch_pair.keys()):
                    f_len = freq.shape[0]
                    for l in range(f_len):
                        f = freq[l]
                        p = psd[k][l]
                        df.loc[len(df)] = [sub, tp, ch, f, p]
            df_save_path = os.path.join(save_path, f'{sub}_psd.xlsx')
            df.to_excel(df_save_path, index=False)

    def highpass_filter(self, data):
        sos = sig.butter(2, self.low_cut, 'highpass', fs=self.fs, output='sos')
        # 零相位数字滤波
        data = sig.sosfiltfilt(sos, data, axis=1)
        return data

    def lowpass_filter(self, data):
        sos = sig.butter(2, self.high_cut, 'lowpass', fs=self.fs, output='sos')
        # 零相位数字滤波
        data = sig.sosfiltfilt(sos, data, axis=1)
        return data

    def calc_band_psd(self, x, y):
        x = x[self.fft_freq_down:self.fft_freq_up + 1]
        y = y[self.fft_freq_down:self.fft_freq_up + 1]

        # 计算功率占比，单位%
        total = y.sum()
        y_norm = (y / total) * 100

        # 恢复 fft 原始长度以方便整数索引
        y_norm = np.concatenate((np.zeros(self.fft_freq_down), y_norm), axis=0)

        # 计算分频段功率占比
        delta = y_norm[self.fft_freq_down:16].sum()         # [0.5, 4)
        theta = y_norm[16:32].sum()                         # [4, 8)
        alpha = y_norm[32:52].sum()                         # [8, 13)
        beta = y_norm[52:self.fft_freq_up + 1].sum()        # [13, 30]

        y_band = np.array([delta, theta, alpha, beta])
        y_norm = y_norm[self.fft_freq_down:self.fft_freq_up + 1]
        return x, y_norm, y_band

    def transpose_info_list(self, info_list):
        # info_list shape [sub, type, (f [freq], p[ch, freq])]
        # result shape [ch, sub, type]
        result = []
        chs = len(self.ch_pair.keys())
        # 多维列表维度转换
        for i in range(chs):
            result.append([])
            for j in range(len(info_list)):
                result[i].append([])
                for k in range(3):
                    # source shape [sub, type, (f [freq], p[ch, freq])]
                    x = info_list[j][k][0]
                    y = info_list[j][k][1][i]
                    x, y_norm, y_band = self.calc_band_psd(x, y)

                    # result shape [ch, sub, type] element (x, y_norm, y_band)
                    result[i][j].append((x, y_norm, y_band))

        # result shape [ch, sub, type] element (x, y_norm, y_band)
        return result

    def calc_average_plot_data(self, result):
        # result shape [ch, sub, type] element (x, y_norm, y_band)
        n_sub = len(self.sub_pair.keys())
        n_ch = len(self.ch_pair.keys())

        # 遍历通道，睡眠类型与个体做功率平均操作
        plot_data = []
        for ch in range(n_ch):
            plot_data.append([])
            for k in range(3):
                x = result[ch][0][k][0]
                y_norm_mean = result[ch][0][k][1]
                y_band_mean = result[ch][0][k][2]

                for j in range(1, n_sub):
                    y_norm_mean += result[ch][j][k][1]
                    y_band_mean += result[ch][j][k][2]
                y_norm_mean /= n_sub
                y_band_mean /= n_sub

                plot_data[ch].append((x, y_norm_mean, y_band_mean))

        # result shape [ch, type] element (x, y_norm, y_band)
        return plot_data

    def plot_and_save_psd(self, plot_data, save_path):
        chs = self.ch_pair.keys()
        save_path = os.path.join(save_path, 'figure')
        os.makedirs(save_path, exist_ok=True)

        LOG.info('正在绘制功率谱密度图')

        for (i, ch) in enumerate(chs):
            label = ch
            # 图片大小
            plt.figure(figsize=(10, 6))
            # 全图属性
            plt.title(f'{label} power spectral')
            # 关闭数据图坐标轴
            plt.axis('off')
            plt.xticks([])
            plt.yticks([])

            # 条形图宽度与坐标偏移
            width = 0.2
            bar_offset_arr = [-0.2, 0, 0.2]
            # 子波频率
            x_band = np.arange(self.cnt_band)
            x_band_label = ['0.5-4', '4-8', '8-13', '13-30']

            # 遍历通道内不同睡眠类型
            for j, c in enumerate(['wake', 'nrem', 'rem']):
                x = plot_data[i][j][0]
                y_norm = plot_data[i][j][1]
                y_band = plot_data[i][j][2]

                # 功率分布百分比折线图
                plt.subplot(1, 2, 1)
                plt.plot(x, y_norm, label=c)
                ax = plt.gca()
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

                # 波段功率占比条形图
                plt.subplot(1, 2, 2)
                plt.bar(x_band + bar_offset_arr[j], y_band, width, label=c)
                ax = plt.gca()
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

                # 更改为对数分贝单位
                # plt.semilogy(x, y, label=c)

            # 设置折线图图标，属性
            # 换颜色可以查询设置 matplotlib 的 cmap
            plt.subplot(1, 2, 1)

            # plt.ylim((1, 1e4))
            # plt.ylabel('PSD [uV^2/Hz]')
            # 设置单位
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Normalized power (%)')
            # 展示网格
            plt.grid(True)
            # 图例
            plt.legend()

            # 设置条形图图标，属性
            plt.subplot(1, 2, 2)

            plt.xticks(x_band, x_band_label)
            plt.xlabel('Frequency Range (Hz)')
            plt.ylabel('Percentage Sum (a.u.)')
            # plt.grid(True)
            plt.legend()

            fig_save_path = os.path.join(save_path, f'psd_{ch}.png')
            plt.savefig(fig_save_path)

            # TODO
            # 展示图片
            plt.show()
            plt.clf()
            plt.close()
