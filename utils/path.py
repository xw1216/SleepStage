import os.path


def get_svg_url(name):
    path = os.path.join(os.getcwd(), 'gui', 'style', 'svg', name + '.svg')
    path = path.replace('\\', '/')
    return path

def epoch_file_ext_name():
    return '_epoch.csv'

def raw_eeg_file_ext_name():
    return '_eeg.smrx'

def data_src_dir():
    return os.path.join(os.getcwd(), 'dataset', 'raw')

def data_tgt_dir():
    os.path.join(os.getcwd(), 'dataset', 'extract')
