from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QPolygonF, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsItem


class QDMCutLine(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.red)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([4, 1])

        self.setZValue(2)

    def boundingRect(self):
        return self.shape().boundingRect()
        # return QRectF(0, 0, 1, 1)

    def shape(self):
        poly = QPolygonF(self.line_points)
        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painter.setPen(self._pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
