import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from kneed import KneeLocator
from PyQt6.QtGui import QPixmap


class Point(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.label = ""
        self.cluster_index = -1


class PointsArray(object):
    def __init__(self):
        self.points = []
        self.__features = []

    def add(self, p: Point):
        self.points.append(p)
        self.__features.append([p.x, p.y])

    def get_features(self):
        return np.array(self.__features)


class Clusterizator(object):
    def __init__(self, pixmap: QPixmap):
        self.__points_array = PointsArray()
        self.__pixmap = pixmap
        self.__prepare_data()
        print("Found points: ", len(self.__points_array.points))
        print("As numpy array: ", self.__points_array.get_features().shape)
        # for i in range(len(self.__points_array.points)):
        #     print("Point: x=", self.__points_array.points[i].x, "y=", self.__points_array.points[i].y)

    def clusterize(self):
        if len(self.__points_array.points) == 0:
            print("No points found, nothing to do")
            return []

        print("Features before: ", self.__points_array.get_features()[:5])
        # preprocess data, so that the features have a mean of 0 and standard deviation of 1
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.__points_array.get_features())
        print("Scaled: ", scaled_features[:5])

        kmeans_kwargs = {
            "init": "random",
            "n_init": 100,
            "max_iter": 3000,
            "random_state": 42,
        }

        # kmeans = KMeans(
        #     init="random",
        #     n_clusters = 3,
        #     n_init = 1000,
        #     max_iter = 3000,
        #     random_state = 42)
        sse = []
        silhouette_coefficients = []
        for i in range(1,20):
            print("precalculate k-means, iteration = ", i)
            kmeans = KMeans(n_clusters=i, **kmeans_kwargs)
            kmeans.fit(scaled_features)
            sse.append(kmeans.inertia_)
            if i > 1:
                score = silhouette_score(scaled_features, kmeans.labels_)
                silhouette_coefficients.append(score)
        # search for elbow point
        print("sse:", sse)
        print("calculate elbow point..")
        knee_locator = KneeLocator(
            range(1, 20), sse, curve = "convex", direction = "decreasing"
        )
        print("knee_locator.elbow:", knee_locator.elbow)
        print("silhouette_coefficients:", silhouette_coefficients)
        print("max:", np.array(silhouette_coefficients).argmax() + 2)

        kmeans = KMeans(n_clusters=knee_locator.elbow, **kmeans_kwargs)
        kmeans.fit(scaled_features)
        print("kmeans.n_clusters:", kmeans.n_clusters)
        print("The lowest SSE value:", kmeans.inertia_)
        print("Final locations of the centroids:", kmeans.cluster_centers_)
        print("The number of iterations required to converge:", kmeans.n_iter_)
        print("the cluster assignments:", kmeans.labels_)

        rs_clusters = []
        for i in range(knee_locator.elbow):
            rs_clusters.append([])
        for i in range(len(kmeans.labels_)):
            cluster_index = kmeans.labels_[i]
            self.__points_array.points[i].cluster_index = cluster_index
            rs_clusters[cluster_index].append(self.__points_array.points[i])

        return rs_clusters

    def __prepare_data(self):
        # 1. transform image to a matrix with values: 0.0 if the color is white, 1.0 if the color is black
        #    (for simplicity, assume that we have only 2 colors in the image)
        transform_func = lambda c: \
            0.0 if c[0][0] == 255 else \
            1.0 if c[0][0] == 0 else \
            (c[0][0] + c[0][1] + c[0][2]) / 3 / 255
        transform_func_vec = np.vectorize(transform_func, signature="(n,m)->()")

        image = self.__pixmap.toImage()
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        # convert the image to vector of color (QColor) arrays consisting of 4 elems (red, green, blue, alpha)
        image_vector = np.asarray(ptr).reshape(image.height() * image.width(), 1, 4)
        # transform color arrays to single float values in a range [0.0, 1.0]
        rs = transform_func_vec(image_vector)
        # transform result vector back to array (matrix) of image size
        rs = rs.reshape(image.height(), image.width())

        # 2. for clusterization we do not need to have a matrix, we need a vector of non-empty (non-white) points,
        #    so now we are transforming the result image matrix into a vector of non-empty points:
        for i in range(image.height()):
            for j in range(image.width()):
                if rs[i,j] != 0.0:
                    self.__points_array.add(Point(j, i))
