from enum import Enum
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPen, QBrush, QMouseEvent, QResizeEvent, QPixmap, QPainter, QColor


class ScenePainterMode(Enum):
    PAINT = 1
    ERASE = 2


class MouseIndicator(object):
    def paint(self, x: int, y: int, scene: QGraphicsScene):
        self.hide(scene)
        return

    def hide(self, scene: QGraphicsScene):
        return


class MouseIndicatorPaint(MouseIndicator):
    def __init__(self):
        self.__line_x = None
        self.__line_y = None

    def paint(self, x: int, y: int, scene: QGraphicsScene):
        self.hide(scene)
        length = 20
        self.__line_x = scene.addLine(x - length / 2, y, x + length / 2, y)
        self.__line_y = scene.addLine(x, y - length / 2, x, y + length / 2)

    def hide(self, scene: QGraphicsScene):
        if self.__line_y is not None:
            scene.removeItem(self.__line_x)
            scene.removeItem(self.__line_y)


class MouseIndicatorErase(MouseIndicator):
    def __init__(self, size: int):
        self.__size = size
        self.__rect = None

    def paint(self, x: int, y: int, scene: QGraphicsScene):
        self.hide(scene)
        self.__rect = scene.addRect(x - self.__size / 2, y - self.__size / 2, self.__size, self.__size)

    def hide(self, scene: QGraphicsScene):
        if self.__rect is not None:
            scene.removeItem(self.__rect)


class ScenePainter(QGraphicsView):
    def __init__(self):
        self.__scene = QGraphicsScene(0, 0, 1024, 768)
        super().__init__(self.__scene)

        self.setMouseTracking(True)
        self.__mouse_pressed = False

        self.__mouse_indicator = MouseIndicatorPaint()
        self.__eraser_size = 20

        self.__mode: ScenePainterMode = ScenePainterMode.PAINT
        self.__mouseX, self.__mouseY = None, None
        self.__bg = None

    def setmode(self, mode: ScenePainterMode):
        self.__mode = mode
        self.__mouse_indicator.hide(self.__scene)
        if mode == ScenePainterMode.PAINT:
            self.__mouse_indicator = MouseIndicatorPaint()
        else:
            self.__mouse_indicator = MouseIndicatorErase(self.__eraser_size)

    def getpixmap(self):
        pixmap = QPixmap(int(self.__scene.width()), int(self.__scene.height()))
        painter = QPainter(pixmap)
        self.__scene.render(painter)
        return pixmap

    def resizeEvent(self, a0: QResizeEvent) -> None:
        super().resizeEvent(a0)
        if self.__bg is not None:
            self.__scene.removeItem(self.__bg)
        self.__scene.setSceneRect(0, 0, self.width(), self.height())
        self.__bg = self.__scene.addRect(0, 0,
                                         int(self.__scene.width()),
                                         int(self.__scene.height()),
                                         QPen(QColor(255, 255, 255, 255)),
                                         QBrush(QColor(255, 255, 255, 255)))
        self.__bg.setZValue(-1)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        mouse_pos = self.mapToScene(a0.pos().x(), a0.pos().y())
        if self.__mouse_pressed:
            if self.__mouseX is not None:
                if self.__mode == ScenePainterMode.PAINT:
                    pen = QPen()
                    pen.setColor(QColor(0, 0, 0, 255))
                    pen.setWidth(2)
                    point_from = self.mapToScene(self.__mouseX, self.__mouseY)
                    self.__scene.addLine(point_from.x(), point_from.y(), mouse_pos.x(), mouse_pos.y(), pen)
                elif self.__mode == ScenePainterMode.ERASE:
                    pen = QPen()
                    pen.setColor(QColor(255, 255, 255, 255))
                    brush = QBrush()
                    brush.setColor(QColor(255, 255, 255, 255))
                    self.__scene.addRect(mouse_pos.x() - self.__eraser_size / 2, mouse_pos.y() - self.__eraser_size / 2,
                                         self.__eraser_size, self.__eraser_size, pen, brush)
                else:
                    print("error: unrecognized mode (", self.__mode, ")")
                    # TODO: how to terminate?
            # self.update()
            self.__mouseX = a0.pos().x()
            self.__mouseY = a0.pos().y()
        self.__mouse_indicator.paint(mouse_pos.x(), mouse_pos.y(), self.__scene)
        super().mouseMoveEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent):
        super().mousePressEvent(a0)
        self.__mouse_pressed = True

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.__mouseX, self.__mouseY = None, None
        self.__mouse_pressed = False
        super().mouseReleaseEvent(a0)
