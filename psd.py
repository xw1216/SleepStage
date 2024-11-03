import os
import numpy as np
import pandas as pd

import scipy.signal as sig
import matplotlib.pyplot as plt


def filter_freq_visualize():
    """
    可视化滤波器目标频谱
    """
    # 10 阶 Butter 滤波器，低通 45 Hz，数据采样率 1000 Hz
    sos = sig.butter(10, 45, 'lowpass', fs=1000, output='sos')
    # 以 10000 的频点的粒度计算频谱
    w, h = sig.sosfreqz(sos, worN=10000, fs=1000)

    # plt.subplot(2, 1, 1)
    # 取对数值得到分贝单位
    db = 20 * np.log10(np.maximum(np.abs(h), 1e-5))
    # 画分贝频谱图
    plt.plot(w[0:2000], db[0:2000])
    plt.grid(True)
    plt.ylabel('Gain [dB]')
    plt.title('Frequency Response')
    plt.show()
    plt.clf()


def lowpass_filter(data):
    """
    低通滤波
    :param data: 波形数据
    :return: 滤波后数据
    """
    # 10 阶 Butter 滤波器，低通 45 Hz，数据采样率 1000 Hz
    sos = sig.butter(10, 45, 'lowpass', fs=1000, output='sos')
    # 零相位数字滤波
    data = sig.sosfiltfilt(sos, data, axis=1)
    return data


def highpass_filter(data):
    """
    高通滤波
    :param data: 波形数据
    :return: 滤波后数据
    """
    # 2 阶 Butter 滤波器，高通 1.0 Hz，数据采样率 1000 Hz
    sos = sig.butter(2, 1.0, 'highpass', fs=1000, output='sos')
    # 零相位数字滤波
    data = sig.sosfiltfilt(sos, data, axis=1)
    return data


def calc_band_psd(x, y):
    start_idx = 1

    x = x[start_idx:]
    y = y[start_idx:]

    # 计算功率占比，单位%
    total = y.sum()
    y_norm = (y / total) * 100

    y_norm = np.concatenate((np.zeros(start_idx), y_norm), axis=0)

    # 计算分频段功率占比
    low_delta = y_norm[start_idx:7].sum()  # [0.25, 2)
    high_delta = y_norm[7:16].sum()  # [2, 4)
    theta = y_norm[16: 40].sum()  # [4, 10)
    alpha = y_norm[40: 81].sum()  # [10, 20]

    y_band = np.array([low_delta, high_delta, theta, alpha])
    y_norm = y_norm[start_idx:]
    return x, y_norm, y_band


def rearrange_and_calc_plot_data(info_list, ch):
    # source shape [sub, type, (f [freq], p[ch, freq])]
    # result shape [ch, sub, type]
    result = []

    # 多维列表维度转换
    for i in range(ch):
        result.append([])
        for j in range(len(info_list)):
            result[i].append([])
            for k in range(3):
                # source shape [sub, type, (f [freq], p[ch, freq])]
                x = info_list[j][k][0]
                y = info_list[j][k][1][i]
                x, y_norm, y_band = calc_band_psd(x, y)

                # result shape [ch, sub, type] element (x, y_norm, y_band)
                result[i][j].append((x, y_norm, y_band))

    # 遍历通道，睡眠类型与个体做功率平均操作
    plot_data = []
    for i in range(ch):
        plot_data.append([])
        for k in range(3):
            x = result[i][0][k][0]
            y_norm_mean = result[i][0][k][1]
            y_band_mean = result[i][0][k][2]

            for j in range(1, len(info_list) - 1):
                y_norm_mean += result[i][j][k][1]
                y_band_mean += result[i][j][k][2]
            y_norm_mean /= len(info_list)
            y_band_mean /= len(info_list)

            plot_data[i].append((x, y_norm_mean, y_band_mean))

    # result shape [ch, type] element (x, y_norm, y_band)
    return plot_data



# 存储计算中间结果
info_list = []

# 文件编号 (修改为需要画图的编号序列)
file_idx = ['01', '02',]

# 常量定义
ch = 0      # 通道数
n_eeg = 2   # 脑电通道数
lim = 80   # 截止频率点计数
fs = 1000.0 # 采样频率
n_sec = 4   # 分段时长

pt_wnd = int(n_sec * fs)  # 时间窗内数据点

for i in range(len(file_idx)):
    info_list.append([])

    # 提取后的数据文件路径
    path = os.path.join('dataset', 'extract', file_idx[i])
    data = os.path.join(path, file_idx[i] + '_wave.npy')
    label = os.path.join(path, file_idx[i] + '_epoch.csv')

    data = np.load(data)
    label = pd.read_csv(label)
    ch = data.shape[0]

    # 高通滤波
    data = highpass_filter(data)

    # 调整数据与张量的形状
    data = data.reshape(ch, -1, pt_wnd)
    label = (label['class'].values - 1).reshape(-1)

    # 将不同类的时间段分离出来
    wake_idx = np.where(label == 0)[0]
    nrem_idx = np.where(label == 1)[0]
    rem_idx = np.where(label == 2)[0]

    # 遍历三种类别的时间段
    for (name, idx) in [
        ('wake', wake_idx),
        ('nrem', nrem_idx),
        ('rem', rem_idx)
    ]:
        # 提取时间段
        wave = data[:, idx, :]
        # 傅里叶变换后频谱图，其中 nfft 指定了频率点粒度
        f, p = sig.periodogram(wave, fs, axis=2, nfft=4000)

        # 选取限定范围内的频率与功率点对
        f = f[1:lim+1]
        p = p[:, :, 1:lim+1]
        p = p.mean(axis=1)
        info_list[i].append((f, p))

# 转换为画图数据
# plot data shape [ch, type] element (x, y_norm, y_band)
plot_data = rearrange_and_calc_plot_data(info_list, ch)

# 遍历通道以作图
for i in range(ch):
    label = f'M{i} {"EEG" if i < n_eeg else "EMG"}'
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
    x_band = np.arange(4)
    x_band_label = ['0.5-2', '2-4', '4-10', '10-20']

    # 遍历通道内不同睡眠类型
    for j, c in enumerate(['wake', 'nrem', 'rem']):
        x = plot_data[i][j][0]
        y_norm = plot_data[i][j][1]
        y_band = plot_data[i][j][2]

        # 功率分布百分比折线图
        plt.subplot(1, 2, 1)
        plt.plot(x, y_norm, label=c)

        # 波段功率占比条形图
        plt.subplot(1, 2, 2)
        plt.bar(x_band + bar_offset_arr[j], y_band, width, label=c)

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

    # 展示图片
    plt.show()
    plt.clf()
    plt.close()
