import os.path


def get_svg_url(name):
    path = os.path.join(os.getcwd(), 'gui', 'style', 'svg', name + '.svg')
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
