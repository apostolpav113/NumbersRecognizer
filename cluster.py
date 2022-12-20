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


# see: https://realpython.com/k-means-clustering-python/
#      https://www.dominodatalab.com/blog/getting-started-with-k-means-clustering-in-python
class Clusterizator(object):
    def __init__(self, pixmap: QPixmap):
        self.__points_array = PointsArray()
        self.__pixmap = pixmap
        self.__progress_callback = None
        self.__prepare_data()

    def set_progress_callback(self, callback):
        self.__progress_callback = callback

    def clusterize(self, auto_find_clusters_count: bool, clusters_count: int):
        # if auto_find_clusters_count is True then clusters_count represents MAX clusters count
        # otherwise it is just the fixed count of clusters to recognize

        if len(self.__points_array.points) == 0 or clusters_count == 0:
            print("No points found, nothing to do")
            return []

        # preprocess data, so that the features have a mean of 0 and standard deviation of 1
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.__points_array.get_features())

        kmeans_kwargs = {
            "init": "random",
            "n_init": 100,
            "max_iter": 3000,
            "random_state": 42,
        }

        nclusters = clusters_count

        if auto_find_clusters_count and clusters_count > 1:
            sse = []
            silhouette_coefficients = []
            max_steps = clusters_count
            for i in range(1, max_steps+1):
                print("precalculate k-means, iteration = ", i)
                if self.__progress_callback is not None and callable(self.__progress_callback):
                    self.__progress_callback(int(i / max_steps * 100))
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
                range(1, max_steps+1), sse, curve="convex", direction="decreasing"
            )
            print("knee_locator.elbow:", knee_locator.elbow)
            print("silhouette_coefficients:", silhouette_coefficients)
            print("max silhouette_coefficients:", np.array(silhouette_coefficients).argmax() + 2)
            if knee_locator.elbow is None:
                print("Elbow point not found")
                return []
            nclusters = knee_locator.elbow

        kmeans = KMeans(n_clusters=nclusters, **kmeans_kwargs)
        kmeans.fit(scaled_features)
        print("kmeans.n_clusters:", kmeans.n_clusters)
        print("The lowest SSE value:", kmeans.inertia_)
        print("Final locations of the centroids:", kmeans.cluster_centers_)
        print("The number of iterations required to converge:", kmeans.n_iter_)
        print("the cluster assignments:", kmeans.labels_)

        # generate results
        rs_clusters = []
        for i in range(nclusters):
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
                if rs[i, j] != 0.0:
                    self.__points_array.add(Point(j, i))
