import os.path
import sys


def get_svg_url(name):
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        path = os.path.join(sys._MEIPASS, 'svg', name + '.svg')
    else:
        path = os.path.join(os.getcwd(), 'svg', name + '.svg')
    path = path.replace('\\', '/')
    return path


def info_file_ext_name():
    return '_info.csv'


def epoch_file_ext_name():
    return '_epoch.csv'


def raw_eeg_file_ext_name():
    return '_eeg.smrx'


def extract_eeg_ext_name():
    return '_wave.npy'


def data_src_dir():
    return os.path.join(os.getcwd(), 'dataset', 'raw')


def data_tgt_dir():
    return os.path.join(os.getcwd(), 'dataset', 'extract')
