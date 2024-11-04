from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontMetrics

app = QApplication([])

# 设置字体和字号
font = QFont("Microsoft Yahei", 14)
font_metrics = QFontMetrics(font)

# 测量字符的宽度
char_width = font_metrics.horizontalAdvance("选")  # 可以替换成任何你想测量的字符

print(f"字符 'A' 的宽度: {char_width} 像素")