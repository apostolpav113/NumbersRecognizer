import tensorflow as tf
import keras
import keras.utils
from keras.layers import Dense, Flatten
from keras.models import Sequential
from keras.datasets import mnist
import numpy as np
import os


class NumbersRecognizer(object):
    def __init__(self):
        os.makedirs("./data", exist_ok=True)
        if os.path.exists("data/xtrain.npy"):
            self.__X_train = np.load("data/xtrain.npy")
            self.__y_train = np.load("data/ytrain.npy")
            self.__X_test = np.load("data/xtest.npy")
            self.__y_test = np.load("data/ytest.npy")
        else:
            (self.__X_train, self.__y_train), (self.__X_test, self.__y_test) = mnist.load_data()
            np.save("data/xtrain", self.__X_train)
            np.save("data/ytrain", self.__y_train)
            np.save("data/xtest", self.__X_test)
            np.save("data/ytest", self.__y_test)

        # normalize input data
        self.__X_train = self.__X_train / 255
        self.__X_test = self.__X_test / 255

        # categorize labels (turn an array [1,0,9,...] into
        #                    [[0,1,0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,1],...])
        self.__y_train = keras.utils.to_categorical(self.__y_train, 10)
        self.__y_test = keras.utils.to_categorical(self.__y_test, 10)

        self.__model = self.__get_model()

        print("Model accuracy:")
        self.__model.evaluate(self.__X_test, self.__y_test)

    def __get_model(self):
        # see https://habr.com/ru/post/705306/

        model_file_path = "data/trained_model"

        if os.path.exists(model_file_path):
            model = keras.models.load_model(model_file_path)
            return model

        # there is no pretrained model, create and train a new one:
        model = Sequential()
        model.add(Dense(32, activation='relu', input_shape=self.__X_train[0].shape))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(256, activation='relu'))
        model.add(Dense(512, activation='relu'))
        model.add(Flatten())
        model.add(Dense(10, activation='sigmoid'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
        model.fit(self.__X_train, self.__y_train, epochs=100)
        model.save(model_file_path)

        return model
