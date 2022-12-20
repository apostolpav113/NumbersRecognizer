import sys
import numpy as np
from functools import partial
from painter import ScenePainter, ScenePainterMode
from cluster import Clusterizator
from numbers_recognition import NumbersRecognizer
import image_converter
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class Application(object):
    def __init__(self, argv, title: str):
        self.__app = QApplication(argv)

        # init main window
        self.__main_window = QMainWindow()
        self.__main_window.setWindowTitle(title)
        screen = self.__app.primaryScreen()
        self.__main_window.resize(int(screen.size().width() * 3 / 5),
                                  int(screen.size().height() * 3 / 5))

        # init painter component
        self.__painter = ScenePainter()
        self.__painter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # init other user interface components
        self.__painter_toolbar = QToolBar()
        self.__painter_toolbar.setIconSize(QSize(16, 16))

        self.__painter_toolbutton_modepaint = QToolButton()
        self.__painter_toolbutton_modepaint.setIcon(QIcon("icons/pencil.png"))
        self.__painter_toolbutton_modepaint.setCheckable(True)
        self.__painter_toolbutton_modepaint.setChecked(True)
        self.__painter_toolbutton_modepaint.clicked.connect(self.__painter_toolbutton_modepaint_clicked)

        self.__painter_toolbutton_modeerase = QToolButton()
        self.__painter_toolbutton_modeerase.setIcon(QIcon("icons/eraser.png"))
        self.__painter_toolbutton_modeerase.setCheckable(True)
        self.__painter_toolbutton_modeerase.clicked.connect(self.__painter_toolbutton_modeerase_clicked)

        self.__painter_toolbutton_clear = QToolButton()
        self.__painter_toolbutton_clear.setIcon(QIcon("icons/cross.png"))
        self.__painter_toolbutton_clear.clicked.connect(self.__painter_toolbutton_clear_clicked)

        self.__painter_toolbar.addWidget(self.__painter_toolbutton_modepaint)
        self.__painter_toolbar.addWidget(self.__painter_toolbutton_modeerase)
        self.__painter_toolbar.addSeparator()
        self.__painter_toolbar.addWidget(self.__painter_toolbutton_clear)

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

        self.__left_panel.layout().addWidget(QLabel("Количество кластеров:"))
        self.__checkbox_auto_clusters = QCheckBox("авто")
        self.__checkbox_auto_clusters.setChecked(True)
        self.__checkbox_auto_clusters.clicked.connect(self.__checkbox_auto_clusters_clicked)
        self.__left_panel.layout().addWidget(self.__checkbox_auto_clusters)
        self.__spinbox_max_clusters = QSpinBox()
        self.__spinbox_max_clusters.setMaximum(100)
        self.__spinbox_max_clusters.setValue(20)
        self.__max_clusters = QWidget()
        self.__max_clusters.setLayout(QHBoxLayout())
        self.__max_clusters.layout().setSpacing(0)
        self.__max_clusters.layout().setContentsMargins(0,0,0,0)
        self.__max_clusters.layout().addWidget(QLabel("Макс. кластеров:"))
        self.__max_clusters.layout().addWidget(self.__spinbox_max_clusters)
        self.__left_panel.layout().addWidget(self.__max_clusters)
        self.__spinbox_fixed_clusters = QSpinBox()
        self.__spinbox_fixed_clusters.setMaximum(100)
        self.__spinbox_fixed_clusters.setValue(1)
        self.__fixed_clusters = QWidget()
        self.__fixed_clusters.setLayout(QHBoxLayout())
        self.__fixed_clusters.layout().setSpacing(0)
        self.__fixed_clusters.layout().setContentsMargins(0, 0, 0, 0)
        self.__fixed_clusters.layout().addWidget(QLabel("Число кластеров:"))
        self.__fixed_clusters.layout().addWidget(self.__spinbox_fixed_clusters)
        self.__left_panel.layout().addWidget(self.__fixed_clusters)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.__left_panel.layout().addWidget(line)
        self.__fixed_clusters.setVisible(False)

        self.__label_result = QLabel()
        self.__left_panel.layout().addWidget(self.__label_result)

        self.__progress_bar = QProgressBar()
        self.__progress_bar.setMaximum(200)
        self.__progress_bar.setVisible(False)
        self.__left_panel.layout().addWidget(self.__progress_bar)

        self.__result_widget = QWidget()
        self.__result_widget.setLayout(QVBoxLayout())
        self.__left_panel.layout().addWidget(self.__result_widget)

        self.__left_panel.layout().addSpacerItem(QSpacerItem(10, 10,
                                                             QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        self.__left_panel.setFixedWidth(200)

        self.__main_layout = QHBoxLayout()
        self.__main_layout.addWidget(self.__left_panel)
        self.__main_layout.addWidget(self.__painter_panel)

        self.__central_widget = QWidget()
        self.__central_widget.setLayout(self.__main_layout)

        self.__main_window.setCentralWidget(self.__central_widget)

        #
        self.__show_result_buttons = []

    def __painter_toolbutton_modepaint_clicked(self):
        self.__painter_toolbutton_modepaint.setChecked(True)
        self.__painter_toolbutton_modeerase.setChecked(False)
        self.__painter.setmode(ScenePainterMode.PAINT)

    def __painter_toolbutton_modeerase_clicked(self):
        self.__painter_toolbutton_modepaint.setChecked(False)
        self.__painter_toolbutton_modeerase.setChecked(True)
        self.__painter.setmode(ScenePainterMode.ERASE)

    def __painter_toolbutton_clear_clicked(self):
        self.__painter.clear()
        self.__remove_result_components()

    def __remove_result_components(self):
        self.__label_result.setText("")
        self.__show_result_buttons = []
        for i in reversed(range(self.__result_widget.layout().count())):
            self.__result_widget.layout().itemAt(i).widget().setParent(None)

    def __enable_components(self, enabled: bool):
        self.__button_recognize.setEnabled(enabled)
        self.__painter_toolbutton_clear.setEnabled(enabled)
        self.__painter_toolbutton_modepaint.setEnabled(enabled)
        self.__painter_toolbutton_modeerase.setEnabled(enabled)
        self.__checkbox_auto_clusters.setEnabled(enabled)
        self.__max_clusters.setEnabled(enabled)
        self.__fixed_clusters.setEnabled(enabled)
        self.__main_window.update()
        self.__app.processEvents()

    def __checkbox_auto_clusters_clicked(self):
        self.__max_clusters.setVisible(self.__checkbox_auto_clusters.isChecked())
        self.__fixed_clusters.setVisible(not self.__max_clusters.isVisible())

    def __progress_callback(self, progress: int):
        self.__progress_bar.setValue(progress)
        self.__app.processEvents()

    def __button_recognize_clicked(self):
        self.__remove_result_components()
        self.__enable_components(False)
        self.__label_result.setText("Кластеризация...")

        self.__progress_bar.setValue(0)
        self.__progress_bar.setVisible(True)

        clusterizator = Clusterizator(self.__painter.getpixmap())
        clusterizator.set_progress_callback(self.__progress_callback)
        auto_clusters = self.__checkbox_auto_clusters.isChecked()
        clusters_count = self.__spinbox_max_clusters.value() if auto_clusters else self.__spinbox_fixed_clusters.value()
        print("clusters_count:", clusters_count)
        self.__clusters = clusterizator.clusterize(auto_clusters, clusters_count)
        cluster_count = len(self.__clusters)

        self.__label_result.setText("Распознавание...")
        self.__app.processEvents()
        numbers_recognizer = NumbersRecognizer()

        self.__cluster_predictions = []
        for i in range(cluster_count):
            converter = image_converter.ImageConverter(self.__clusters[i])
            self.__cluster_predictions.append(numbers_recognizer.do_predict(converter.get_data()))
            self.__progress_callback(int(100 + i/cluster_count*100))

        self.__label_result.setText("Найдено кластеров: " + str(cluster_count))

        self.__enable_components(True)
        self.__progress_bar.setVisible(False)

        if cluster_count == 0:
            return

        for i in range(cluster_count):
            widget = QWidget()
            widget.setLayout(QHBoxLayout())
            labels_widget = QWidget()
            labels_widget.setLayout(QVBoxLayout())
            label = QLabel("Кластер " + str(i+1))
            label_prediction = QLabel("Прогноз: " + str(np.argmax(self.__cluster_predictions[i])))
            labels_widget.layout().addWidget(label)
            labels_widget.layout().addWidget(label_prediction)
            widget.layout().addWidget(labels_widget)
            button = QToolButton()
            button.setCheckable(True)
            button.setIcon(QIcon("icons/light-bulb-off.png"))
            button.setProperty("number", i)
            button.clicked.connect(partial(self.show_cluster, i))

            self.__show_result_buttons.append(button)

            widget.layout().addWidget(button)
            self.__result_widget.layout().addWidget(widget)

    def show_cluster(self, index):
        self.__painter.highlight_points(self.__clusters[index])
        print("Prediction:", self.__cluster_predictions[index])
        print("Prediction argmax:", np.argmax(self.__cluster_predictions[index]))
        self.__show_result_buttons[index].setIcon(QIcon("icons/light-bulb.png"))
        for i in range(len(self.__show_result_buttons)):
            if i == index:
                continue
            self.__show_result_buttons[i].setChecked(False)
            self.__show_result_buttons[i].setIcon(QIcon("icons/light-bulb-off.png"))

    def run(self):
        self.__main_window.show()
        self.__app.exec()


if __name__ == '__main__':
    app = Application(sys.argv, "Numbers recognizer v0.0.1")
    app.run()
