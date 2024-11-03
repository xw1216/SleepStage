import os.path


def get_svg_url(name):
    path = os.path.join(os.getcwd(), 'gui', 'style', 'svg', name + '.svg')
    path = path.replace('\\', '/')
    return path