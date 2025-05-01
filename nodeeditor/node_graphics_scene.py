import math

from PySide6.QtCore import QLine, Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsScene


class QDMGraphicsScene(QGraphicsScene):
    itemSelected = Signal()
    itemsDeselected = Signal()
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        # settings
        self.grid_size = 25
        self.grid_squares = 5

        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidthF(1.0)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidthF(1.5)

        self.setBackgroundBrush(self._color_background)

    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if 0 != x % (self.grid_size * self.grid_squares): lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if 0 != y % (self.grid_size * self.grid_squares): lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))


        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(lines_dark)