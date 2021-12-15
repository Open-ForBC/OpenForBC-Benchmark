#!/usr/bin/env python

import tensorflow as tf
import tensorflow.keras as keras
# import matplotlib.pyplot as plt
import time
import sys
from timeit import default_timer as timer
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from keras.utils.np_utils import to_categorical
from functools import reduce
from tensorflow.keras.datasets import mnist
from sklearn.metrics import accuracy_score

input_size = 28*28
output_size = 10
n_epochs = 10


# READ FROM COMMAND LINE DEVICE, NETWORK SIZE AND BATCH SIZE

# CHECK GPU AVAILABILITY

if tf.config.list_physical_devices('GPU') == 0:
    print("GPU unavailable :(")
    sys.exit(0)

# READ ARGS FROM COMMAND LINE
# Raise error if correct arguments aren't given
if len(sys.argv) != 4:
    print("Matmul benchmark need 3 arguments:")
    print("- Device")
    print("- Shallow Layer dimension")
    print("- Batch size")
    sys.exit(1)

hidden_layer_list = []  # This list is read from the settings file

dev = sys.argv[1]
hidden_layer_list.append(int(sys.argv[2]))
batch_size = int(sys.argv[3])

# SET DEVICE

if dev == 'cpu':
    d = '/cpu:0'
elif dev == 'gpu':
    if tf.config.list_physical_devices('GPU') == 0:
        print("GPU unavailable :(")
        sys.exit(0)
    d = '/device:GPU:0'


# Timing callback definition
class TimeHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.batch_times = []
        self.epoch_times = []
        self.training_time = []
        self.training_time_start = time.time()

    def on_batch_begin(self, batch, logs={}):
        self.batch_time_start = time.time()

    def on_batch_end(self, batch, logs={}):
        self.batch_times.append(time.time() - self.batch_time_start)

    def on_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = time.time()

    def on_epoch_end(self, batch, logs={}):
        self.epoch_times.append(time.time() - self.epoch_time_start)

    def on_train_end(self, batch, logs={}):
        self.training_time.append(time.time() - self.training_time_start)


# Data loading method
def data_loading(output):
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # Data preprocessing: I have to rescale and flatten all the images
    shape = (28, 28)
    shape_l = reduce(lambda a, b: a*b, shape)
    x_train = x_train.reshape((-1, shape_l)) / 255.
    x_test = x_test.reshape((-1, shape_l)) / 255.
    # One-hot encoding
    y_train = to_categorical(y_train, num_classes=output)
    y_test = to_categorical(y_test, num_classes=output)
    return (x_train, y_train), (x_test, y_test)


# Model defintion method
def model_def(hidden_layer, input, output):
    model = Sequential()
    for i in range(len(hidden_layer)+1):
        if i == 0:
            model.add(Dense(hidden_layer[i], activation='relu',
                      input_shape=(input_size,)))
        elif i == len(hidden_layer):
            model.add(Dense(output_size, activation='softmax'))
        else:
            model.add(Dense(hidden_layer[i], activation='relu'))
    loss = keras.losses.CategoricalCrossentropy()
    optim = keras.optimizers.SGD(learning_rate=0.01, momentum=0.05)
    metrics = ["accuracy"]
    model.compile(loss=loss, optimizer=optim, metrics=metrics)
    return model


def main():
    (X_train, Y_train), (X_test, Y_test) = data_loading(output_size)
    nn = model_def(hidden_layer_list, input_size, output_size)
    nn.summary()

    # TRAINING

    time_callback = TimeHistory()
    print("Training...")
    nn = model_def(hidden_layer_list, input_size, output_size)
    begin = timer()  # Duration of the whole fit() method run
    # history = nn.fit(X_train, Y_train, epochs=n_epochs, batch_size=batch_size,
    #                  callbacks=[time_callback], validation_split=0.3, verbose=0)
    nn.fit(X_train, Y_train, epochs=n_epochs, batch_size=batch_size,
           callbacks=[time_callback], validation_split=0.3, verbose=0)
    training_time = timer() - begin  # Duration of the whole fit() method run
    training_time_sum_over_batches = sum(time_callback.batch_times)
    time_per_sample = training_time_sum_over_batches/((len(X_train)//batch_size)
                                                      * batch_size)
    sample_per_second = 1./time_per_sample

    # TESTING IN-SAMPLE

    print("Testing in-sample...")
    # Evaluate the model in-sample
    begin = timer()  # Inference time on training set
    pred = nn.predict(X_train).argmax(1)
    testing_time_insample = timer() - begin  # Inference time on training set
    # test_accuracy_in_sample = accuracy_score(Y_train.argmax(1),
    #                                          pred, normalize=False)/len(X_train)
    accuracy_score(Y_train.argmax(1),
                   pred, normalize=False)/len(X_train)
    time_per_sample_test_insample = testing_time_insample/len(X_train)
    sample_per_second_test_insample = 1./time_per_sample_test_insample

    # TESTING OUT-OF-SAMPLE

    print("Testing out-of-sample...")
    # Evaluate the model out-of-sample
    begin = timer()  # Inference time on training set
    pred = nn.predict(X_test).argmax(1)
    testing_time_outofsample = timer() - begin  # Inference time on training set
    # test_accuracy_out_of_sample = accuracy_score(Y_test.argmax(1),
    #                                              pred, normalize=False)/len(X_test)
    accuracy_score(Y_test.argmax(1),
                   pred, normalize=False)/len(X_test)
    time_per_sample_test_outofsample = testing_time_outofsample/len(X_test)
    sample_per_second_test_outofsample = 1./time_per_sample_test_outofsample

    # # DISPLAY RESULTS #

    # # Accuracy Report
    # fig = plt.figure(facecolor='white')
    # fig.set_figheight(6)
    # fig.set_figwidth(6)
    # plt.bar(-1, test_accuracy_in_sample, label='In-sample accuracy')
    # plt.bar(1, test_accuracy_out_of_sample, label='Out-of-sample accuracy')
    # plt.title('Model Accuracy')
    # plt.ylabel('accuracy')
    # plt.legend(loc='right', bbox_to_anchor=(1.15, 0.1),
    #            fancybox=True, shadow=True, ncol=1)

    # # Learning curves
    # fig = plt.figure(facecolor='white')
    # fig.set_figheight(6)
    # fig.set_figwidth(6)
    # plt.plot(history.history['accuracy'])
    # plt.plot(history.history['val_accuracy'])
    # plt.title('Learning Curves')
    # plt.ylabel('Accuracy')
    # plt.xlabel('epoch')
    # plt.legend(['In-sample accuracy', 'Validation accuracy'], loc='upper left')

    print("Training the model took %s seconds" % training_time)

    print("Sample processing time during training: %s sample/seconds"
          % sample_per_second)

    print("Training duration summing batch processing time: %s seconds"
          % training_time_sum_over_batches)

    print("Testing the model in-sample took %s seconds" % testing_time_insample)

    print("Sample processing time during inference in-sample: %s sample/seconds"
          % sample_per_second_test_insample)

    print("Testing the model out-of-sample took %s seconds" % testing_time_outofsample)

    print("Sample processing time during inference out-of-sample: %s sample/seconds"
          % sample_per_second_test_outofsample)

    return 0


if __name__ == "__main__":
    with tf.device(dev):
        main()
