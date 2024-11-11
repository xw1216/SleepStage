import os

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from utils.log import LOG


def plot_and_save_psd(chs: list[str], plot_data, save_path):
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
        band_label = ('0.5-4', '4-8', '8-13', '13-30')
        x_band_label = list(band_label)
        x_band = np.arange(len(band_label))

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

        # clean plot caches
        plt.close('all')
        plt.clf()
        plt.cla()