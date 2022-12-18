import sys
import numpy as np
from painter import ScenePainter

from PyQt6.QtWidgets import *


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
    app = Application(sys.argv, "Numbers recognizer v0.0.1")
    app.run()
