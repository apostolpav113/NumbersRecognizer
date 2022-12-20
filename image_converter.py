from scipy.ndimage import center_of_mass
import cv2
import math
import numpy as np
from PyQt6.QtGui import QPainter, QPixmap, QPen, QImage, QColor, QBrush
from PyQt6 import QtCore



class ImageConverter(object):
    def __init__(self, points):
        self.__image = self.__get_image_for_points(points)
        # mnist images of numbers are 28x28, but the pictures themselves are contained in the centre rectangle 20x20
        self.__image = self.__scale_image(self.__image, 20, 20)
        self.__data_array = self.__prepare_image_for_mnist(self.__image)

    def get_image(self):
        return self.__image

    def get_data(self):
        return self.__data_array

    def __get_image_for_points(self, points):
        # 1. Get min and max coordinates
        min_x, min_y = points[0].x, points[0].y
        max_x, max_y = points[0].x, points[0].y
        for i in range(len(points)):
            if points[i].x < min_x:
                min_x = points[i].x
            if points[i].y < min_y:
                min_y = points[i].y
            if points[i].x > max_x:
                max_x = points[i].x
            if points[i].y > max_y:
                max_y = points[i].y

        # 2. Shift all pointes to the 0-point of coordinates axes
        shifted_coords = []
        for i in range(len(points)):
            shifted_coords.append([points[i].x - min_x, points[i].y - min_y])

        width = max_x - min_x
        height = max_y - min_y

        # 3. Finally, draw an image
        pixmap = QPixmap(width, height)
        painter = QPainter(pixmap)
        pen = QPen(QColor(0, 0, 0, 255))
        pen.setWidth(2)
        brush = QBrush(QColor(255, 255, 255, 255))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.fillRect(0, 0, width, height, brush)
        for i in range(len(shifted_coords)):
            painter.drawPoint(shifted_coords[i][0], shifted_coords[i][1])
        painter.end()

        return QImage(pixmap)

    def __scale_image(self, image: QImage, width: int, height: int):
        image = image.scaled(width, height,
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.SmoothTransformation)
        return image

    def __shift_image_to_center_of_mass(self, img):
        cy, cx = center_of_mass(img)
        rows, cols = img.shape
        shiftx = np.round(cols / 2.0 - cx).astype(int)
        shifty = np.round(rows / 2.0 - cy).astype(int)

        rows, cols = img.shape
        m = np.float32([[1, 0, shiftx], [0, 1, shifty]])
        shifted = cv2.warpAffine(img, m, (cols, rows))
        return shifted

    def __prepare_image_for_mnist(self, image: QImage):
        if image.width() > 20 or image.height() > 20:
            raise Exception("Wrong image size! It should be 20x20 maximum!")

        transform_func = lambda c: int(255 - (int(c[0][0]) + int(c[0][1]) + int(c[0][2])) / 3)
        transform_func_vec = np.vectorize(transform_func, signature="(n,m)->()")

        threshold_func = lambda c: 255 if c >= 64 else 0
        threshold_func_vec = np.vectorize(threshold_func)

        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        # convert the image to vector of color (QColor) arrays consisting of 4 elems (red, green, blue, alpha)
        image_vector = np.asarray(ptr).reshape(image.height() * image.width(), 1, 4)

        rs = transform_func_vec(image_vector)
        rs = threshold_func_vec(rs)
        rs = rs / 255.0
        # transform result vector back to array (matrix) of image size
        rs = rs.reshape(image.height(), image.width())

        rows, cols = rs.shape
        cols_padding = (int(math.ceil((28 - cols) / 2.0)), int(math.floor((28 - cols) / 2.0)))
        rows_padding = (int(math.ceil((28 - rows) / 2.0)), int(math.floor((28 - rows) / 2.0)))
        rs = np.lib.pad(rs, (rows_padding, cols_padding), 'constant')

        rs = self.__shift_image_to_center_of_mass(rs)

        return np.array(rs).reshape(-1, 28, 28, 1)
