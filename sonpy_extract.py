import os
import shutil
import logging

import numpy as np
import pandas as pd
from sonpy import lib as sp


def read_meta_info(handle):
    """
    从 smrx 文件中中读取元信息
    :param handle: 文件句柄
    :return: (数据信息, 数据点是否齐整)
    """
    pts = 0
    info = []
    uneven = False
    # 遍历 4 个通道
    for ch in range(n_ch):
        if handle.ChannelType(ch) == sp.DataType.Adc:

            # 小段持续时间
            sec_t = n_sec
            # 采样率
            fs = round(1 / handle.GetTimeBase())

            # 检测数据点不整齐的情况
            if ch > 0 and pts != handle.ChannelMaxTime(ch):
                uneven = False
            pts = handle.ChannelMaxTime(ch)

            info.append(
                {
                    'name': handle.GetChannelTitle(ch),
                    'pts': pts,
                    'fs': fs,
                    'sec_len': sec_t * fs
                }
            )
    return info, uneven


def read_error(data, pts):
    """
    检测分类数据读出过程中可能发生的错误
    :param data: 波形数据张量
    :param pts: 数据点数量
    :return: 读出是否正确
    """
    if len(data) == 1 and data[0] < 0:
        log.error(f'Error reading data {src_path}: {sp.GetErrorString(int(data[0]))}')
        return False
    elif len(data) == 0:
        log.warning('No data to read')
        return False
    elif len(data) != pts:
        log.warning(f'Bad number of points read, expected {pts} but got {len(data)}')
        return False
    return True


def read_data(handle, pts):
    """
    读出波形数据点
    :param handle: 文件句柄
    :param pts: 数据点数量
    :return: 波形数据张量
    """
    wave = np.empty(shape=(0, pts))
    for ch in range(n_ch):
        data = handle.ReadFloats(ch, pts, 0)
        succ = read_error(data, pts)
        if not succ:
            return None
        else:
            data = data.reshape(1, pts)
            wave = np.concatenate((wave, data), axis=0)
    return wave


# 常量定义
n_ch = 4
n_sec = 4

# 父目录
data_dir = os.path.join('dataset')

# 结果目录
target_dir = os.path.join(data_dir, 'extract')

# 源数据路径
data_dir = os.path.join(data_dir, 'raw')

# 日志
log = logging.getLogger()
log.setLevel(logging.INFO)

# 建立新文件夹
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)

files_all = os.listdir(data_dir)
os.makedirs(target_dir)

# 检测 smrx 文件
files_data = []
for f in files_all:
    if len(f.split('.')) != 2:
        continue
    [name, ext] = f.split('.')
    csv_f = name.split('_')[0] + '_epoch.csv'
    if ext == 'smrx' and csv_f in files_all:
        files_data.append(f)
log.info(f'detected intact data {files_data}')

# 遍历所有 smrx
for f in files_data:
    src_path = os.path.join(data_dir, f)
    log.info(f'Handling file {src_path}')

    handle = sp.SonFile(src_path, True)
    if handle.GetOpenError() != 0:
        log.error(f'Error opening file {src_path}: {sp.GetErrorString(handle.GetOpenError())}')
        quit(1)

    # 读取元数据
    info, uneven = read_meta_info(handle)
    df = pd.DataFrame(info)
    if uneven:
        log.warning(f'Channels is uneven in {src_path}')
        continue

    # 提取数据点
    data = read_data(handle, info[0]['pts'])
    if data is None:
        continue

    idx = f.split('_')[0]
    dst_path = os.path.join(target_dir, f'{idx}')
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    # 保存数据
    np.save(os.path.join(dst_path, f'{idx}_wave.npy'), data)
    df.to_csv(os.path.join(dst_path, f'{idx}_info.csv'), index=False)
    shutil.copy(os.path.join(data_dir, f'{idx}_epoch.csv'),
                os.path.join(dst_path, f'{idx}_epoch.csv'))
    log.info(f'Extract success')
