from PySide6.QtGui import QIcon
import qtawesome as qta

from gui.style.theme import ICON_PATTERN


class IconBank:
    def __init__(self):
        qta.set_defaults(**ICON_PATTERN)

    @classmethod
    def qta(cls, *name: str, **kwargs) -> QIcon:
        """
        :param name: Glyph names are specified by strings, of the form `prefix.name`.
        The `prefix` corresponds to the font to be used and `name` is the name of the icon.
        :param kwargs: referenced to https://qtawesome.readthedocs.io/en/latest/_generate/qtawesome.icon.html
        :return:
        """
        return qta.icon(*name, **kwargs)


ICONS = IconBank()
