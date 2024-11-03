from PySide6.QtGui import QColor

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
}

ICON_PATTERN = {
    'scale_factor': 1.0,
    'color': QColor.fromString('#404040'),
    'color_disabled': QColor.fromString('#dcdcdc'),
    'color_selected': QColor.fromString('#00bcd4')
}
