import sys
from enum import Enum

import numpy as np

# from PyQt6 import QtGui
from PyQt6.QtWidgets import *
# QApplication, QWidget, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, \
# QSizePolicy, QGraphicsScene, QGraphicsView, QToolButton, QSpacerItem
from PyQt6.QtGui import *  # QScreen, QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import *  # Qt, QRect


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


# class Painter(QWidget):
#     def __init__(self):  # , width: int, height: int):
#         super().__init__()
#         # self.resize(200, 200)
#         self.__canvas = QPixmap(self.width(), self.height())
#         self.__drawMy()
#         # self.setPixmap(self.__canvas)
#         self.__mouseX, self.__mouseY = None, None
#
#     def resizeEvent(self, a0: QResizeEvent) -> None:
#         super().resizeEvent(a0)
#         print("resize:", a0)
#         old_canvas = QPixmap(self.__canvas)
#         self.__canvas = QPixmap(self.width(), self.height())
#         painter = QPainter(self.__canvas)
#         painter.fillRect(0, 0, self.__canvas.width() - 1, self.__canvas.height() - 1, QColor("white"))
#         painter.drawPixmap(0, 0, old_canvas.width(), old_canvas.height(), old_canvas)
#         painter.end()
#
#     def mouseMoveEvent(self, a0: QMouseEvent) -> None:
#         if self.__mouseX is not None:
#             painter = QPainter(self.__canvas)
#             pen = QPen()
#             pen.setWidth(2)
#             painter.setPen(pen)
#             painter.drawLine(self.__mouseX, self.__mouseY, a0.pos().x(), a0.pos().y())
#             painter.end()
#             self.update()
#         self.__mouseX = a0.pos().x()
#         self.__mouseY = a0.pos().y()
#         super().mouseMoveEvent(a0)
#
#     def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
#         self.__mouseX, self.__mouseY = None, None
#         super().mouseReleaseEvent(a0)
#
#     def paintEvent(self, a0: QPaintEvent) -> None:
#         painter = QPainter(self)
#         painter.drawPixmap(0, 0, self.__canvas)
#         painter.end()
#         super().paintEvent(a0)
#
#     def __drawMy(self):
#         painter = QPainter(self.__canvas)
#
#         # brush = QBrush()
#         # brush.setColor(QColor("green"))
#         # painter.setBrush(brush)
#         painter.fillRect(0, 0, self.__canvas.width() - 1, self.__canvas.height() - 1, QColor("white"))
#
#         pen = QPen()
#         pen.setWidth(2)
#         pen.setColor(QColor("red"))
#         painter.setPen(pen)
#         font = QFont()
#         font.setPointSize(30)
#         painter.setFont(font)
#         painter.drawText(0, 0, 200, 100, Qt.AlignmentFlag.AlignCenter, "Hello world!")
#         painter.end()


class Application(object):
    def __init__(self, argv, title: str):
        self.__app = QApplication(argv)
        self.__main_window = QMainWindow()
        self.__main_window.setWindowTitle(title)
        screen = self.__app.primaryScreen()
        self.__main_window.resize(int(screen.size().width() * 3 / 5),
                                  int(screen.size().height() * 3 / 5))

        self.__painter = ScenePainter()
        self.__painter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.__painter_toolbar = QToolBar()
        self.__painter_toolbar.setFixedHeight(40)
        # self.__painter_toolbar_layout = QHBoxLayout()
        # self.__painter_toolbar.setLayout(self.__painter_toolbar_layout)
        self.__painter_toolbutton_modepaint = QToolButton()
        self.__painter_toolbutton_modepaint.setText("Paint")
        self.__painter_toolbutton_modepaint.setFixedWidth(30)
        self.__painter_toolbutton_modepaint.setFixedHeight(28)
        self.__painter_toolbutton_modepaint.clicked.connect(self.__painter_toolbutton_modepaint_clicked)
        self.__painter_toolbutton_modeerase = QToolButton()
        self.__painter_toolbutton_modeerase.setText("Erase")
        self.__painter_toolbutton_modeerase.setFixedWidth(30)
        self.__painter_toolbutton_modeerase.setFixedHeight(28)
        self.__painter_toolbutton_modeerase.clicked.connect(self.__painter_toolbutton_modeerase_clicked)
        self.__painter_toolbar.addWidget(self.__painter_toolbutton_modepaint)
        self.__painter_toolbar.addWidget(self.__painter_toolbutton_modeerase)
        # self.__painter_toolbar_layout.addWidget(self.__painter_toolbutton_modepaint)
        # self.__painter_toolbar_layout.addWidget(self.__painter_toolbutton_modeerase)
        # self.__painter_toolbar_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding))

        self.__painter_panel = QWidget()
        self.__painter_layout = QVBoxLayout()
        self.__painter_layout.addWidget(self.__painter_toolbar)
        self.__painter_layout.addWidget(self.__painter)
        self.__painter_panel.setLayout(self.__painter_layout)

        self.__left_panel = QWidget()
        self.__left_panel.setLayout(QVBoxLayout())
        self.__button_recognize = QPushButton()
        self.__button_recognize.setText("Распознать")
        self.__left_panel.layout().addWidget(self.__button_recognize)
        self.__left_panel.layout().addSpacerItem(QSpacerItem(10, 10, vPolicy=QSizePolicy.Policy.Expanding))
        self.__left_panel.setFixedWidth(200)

        self.__main_layout = QHBoxLayout()
        self.__main_layout.addWidget(self.__left_panel)
        self.__main_layout.addWidget(self.__painter_panel)

        self.__central_widget = QWidget()
        self.__central_widget.setLayout(self.__main_layout)

        self.__main_window.setCentralWidget(self.__central_widget)

    def __painter_toolbutton_modepaint_clicked(self):
        print("set paint mode")
        self.__painter.setmode(ScenePainterMode.PAINT)

    def __painter_toolbutton_modeerase_clicked(self):
        print("set erase mode")
        self.__painter.setmode(ScenePainterMode.ERASE)

    def run(self):
        self.__main_window.show()
        self.__app.exec()

        pixmap = self.__painter.getpixmap()
        pixmap.save("test.png")

        image = pixmap.toImage()

        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())

        # transform_func = lambda c: \
        #         0.0 if c[0][0] == 255 and c[0][1] == 255 and c[0][2] == 255 else \
        #         1.0 if c[0][0] == 0 and c[0][1] == 0 and c[0][2] == 0 else \
        #         (c[0][0] + c[0][1] + c[0][2]) / 3 / 255
        transform_func = lambda c: \
            0.0 if c[0][0] == 255 else \
            1.0 if c[0][0] == 0 else \
            (c[0][0] + c[0][1] + c[0][2]) / 3 / 255

        transform_func_vec = np.vectorize(transform_func, signature="(n,m)->()")

        arr = np.asarray(ptr).reshape(image.height() * image.width(), 1, 4)
        rsarr1 = transform_func_vec(arr)
        rsarr1 = rsarr1.reshape(image.height(), image.width())
        print(rsarr1.shape)
        # rsarr = np.array(list(map(
        #     transform_func,
        #     arr)))
        # rsarr = rsarr.reshape(image.height(), image.width())
        for i in range(image.width()):
            print(i, rsarr1[2][i])


if __name__ == '__main__':
    app = Application(sys.argv, "Hello Qt World!")
    app.run()
