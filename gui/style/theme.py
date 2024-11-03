import os.path
import sys

from PySide6.QtGui import QColor

from utils.path import get_svg_url

THEME_EXTRA = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',
    # Font
    'font_family': 'Roboto',
    # Density
    'density_scale': '0',
    # Button Shape
    'button_shape': 'default',
    'font_size': 14,
}

ICON_PATTERN = {
    'scale_factor': 1.0,
    'color': QColor.fromString('#404040'),
    'color_disabled': QColor.fromString('#dcdcdc'),
    'color_selected': QColor.fromString('#00bcd4')
}

NAV_LABEL_FONT_SIZE = 16

NAV_LABEL_STYLE = f'''
    QLabel{{
    font-size: {NAV_LABEL_FONT_SIZE}px;
    margin: 10px 0 5px 0;
}}
'''

LISTVIEW_INDICATOR_STYLE = f'''
QListView::indicator:checked,
QListView::indicator:checked:selected,
QListView::indicator:checked:focus {{
  image: url({get_svg_url('checkbox_checked')});
}}

QListView::indicator:checked:selected:active {{
  image: url({get_svg_url('checkbox_checked_invert')});
}}

QListView::indicator:checked:disabled {{
  image: url({get_svg_url('checkbox_checked_disable')});
}}

QListView::indicator:unchecked,
QListView::indicator:unchecked:selected,
QListView::indicator:unchecked:focus {{
  image: url({get_svg_url('checkbox_unchecked')});
}}

QListView::indicator:unchecked:selected:active {{
  image: url({get_svg_url('checkbox_unchecked_invert')});
}}

QListView::indicator:unchecked:disabled {{
  image: url({get_svg_url('checkbox_unchecked_disable')});
}}
'''


if sys.platform == 'win32':
    THEME_EXTRA['font_family'] = 'Microsoft Yahei'
