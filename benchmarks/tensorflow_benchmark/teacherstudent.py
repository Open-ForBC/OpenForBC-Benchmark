#!/usr/bin/env python
# Copyright (c) 2021-2022 Istituto Nazionale di Fisica Nucleare
# SPDX-License-Identifier: MIT
# Authors:
# - Alessio Borriero <aleborri97@gmail.com>, 2021-2022
# - Daniele Monteleone <daniele.monteleone@to.infn.it>, 2022
# - Gabriele Gaetano Fronze' <gabriele.fronze@to.infn.it>, 2022


import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from keras.utils.np_utils import to_categorical

from base import Benchmark


# Global variables definition
batch_size = 1
n_epochs = 1
n_epochs_training = 200
n_of_class = 10
N = 150
teacher_size = 8

net_size = 2000
input_shape = 20000


def generate_data(input_shape_X, N, n_of_class):
    initializer = keras.initializers.RandomNormal(mean=0.0, stddev=1.0)
    teacher = keras.Sequential()
    teacher.add(
        Dense(
            teacher_size,
            activation="sigmoid",
            kernel_initializer=initializer,
            input_shape=(input_shape_X,),
        )
    )
    teacher.add(Dense(n_of_class, activation="softmax"))
    # Random Data generation
    data = tf.random.normal((N, input_shape_X), 0, 1)
    labels = teacher.predict(data).argmax(1)
    labels = tf.convert_to_tensor(labels)

    labels = to_categorical(labels, num_classes=n_of_class)

    return data, labels


def create_model(input_shape_X):
    model = Sequential()

    if net_size == 0:
        model.add(Dense(n_of_class, activation="softmax", input_shape=(input_shape_X,)))
    else:
        model.add(Dense(net_size, activation="sigmoid", input_shape=(input_shape_X,)))
        model.add(Dense(n_of_class, activation="softmax"))

    loss = keras.losses.CategoricalCrossentropy()
    optim = keras.optimizers.SGD(learning_rate=0.01, momentum=0.05)
    metrics = ["accuracy"]
    model.compile(loss=loss, optimizer=optim, metrics=metrics)

    return model


if __name__ == "__main__":
    bench = Benchmark("MNIST")
    bench.set_data(*generate_data(input_shape, N, n_of_class))
    bench.set_model(create_model(input_shape))
    bench.run()
