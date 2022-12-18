import sys
import numpy as np
from painter import ScenePainter, ScenePainterMode
from cluster import Clusterizator
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
        self.__button_recognize.clicked.connect(self.__button_recognize_clicked)
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
        self.__painter.setmode(ScenePainterMode.PAINT)

    def __painter_toolbutton_modeerase_clicked(self):
        self.__painter.setmode(ScenePainterMode.ERASE)

    def __button_recognize_clicked(self):
        clusterizator = Clusterizator(self.__painter.getpixmap())
        clusterizator.clusterize()

    def run(self):
        self.__main_window.show()
        self.__app.exec()


if __name__ == '__main__':
    app = Application(sys.argv, "Numbers recognizer v0.0.1")
    app.run()
