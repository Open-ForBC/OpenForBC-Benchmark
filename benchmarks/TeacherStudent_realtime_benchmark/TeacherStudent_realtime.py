#!/usr/bin/env python

# Copyright 2021-2022 Open ForBC for the benefit of INFN.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Alessio Borriero <aleborri97@gmail.com>, 2021-2022
# - Daniele Monteleone <daniele.monteleone@to.infn.it>, 2022
# - Gabriele Gaetano Fronze' <gabriele.fronze@to.infn.it>, 2022

import time
import sys
import numpy as np
from datetime import datetime
import argparse
import signal
import nvidia_smi
import GPUtil
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from keras.utils.np_utils import to_categorical


"""
Global variables definition
"""
batch_size = 1
n_epochs = 1
n_epochs_training = 200
n_of_class = 10
N = 150
teacher_size = 8
gpu_performance_sampling_time = 1


class GPUstatistics(keras.callbacks.Callback):
    """
    A set of custom Keras callbacks to monitor Nvidia GPUs load
    """
    def on_train_begin(self, logs={}):
        self.gpu_load = []
        self.gpu_mem = []

    def on_predict_begin(self, logs={}):
        self.gpu_load = []
        self.gpu_mem = []

    def on_predict_batch_begin(self, batch, logs={}):
        res = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
        self.gpu_load.append(res.gpu)
        self.gpu_mem.append(res.memory)

    def on_predict_batch_end(self, batch, logs={}):
        res = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
        self.gpu_load.append(res.gpu)
        self.gpu_mem.append(res.memory)

    def on_train_batch_begin(self, batch, logs={}):
        res = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
        self.gpu_load.append(res.gpu)
        self.gpu_mem.append(res.memory)

    def on_train_batch_end(self, batch, logs={}):
        res = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
        self.gpu_load.append(res.gpu)
        self.gpu_mem.append(res.memory)


class TimeHistory(keras.callbacks.Callback):
    """
    A set of custom Keras callbacks to monitor Nvidia GPUs compute time
    """
    def on_train_begin(self, logs={}):
        self.batch_times = []
        self.epoch_times = []
        self.training_time = []
        self.training_time_start = time.time()

    def on_predict_begin(self, logs={}):
        self.batch_times = []
        self.epoch_times = []
        self.training_time = []
        self.training_time_start = time.time()

    def on_train_batch_begin(self, batch, logs={}):
        self.batch_time_start = time.time()

    def on_train_batch_end(self, batch, logs={}):
        self.batch_times.append(time.time() - self.batch_time_start)

    def on_train_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = time.time()

    def on_train_epoch_end(self, batch, logs={}):
        self.epoch_times.append(time.time() - self.epoch_time_start)

    def on_train_end(self, batch, logs={}):
        self.training_time.append(time.time() - self.training_time_start)

    def on_predict_batch_begin(self, batch, logs={}):
        self.batch_time_start = time.time()

    def on_predict_batch_end(self, batch, logs={}):
        self.batch_times.append(time.time() - self.batch_time_start)

    def on_predict_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = time.time()

    def on_predict_epoch_end(self, batch, logs={}):
        self.epoch_times.append(time.time() - self.epoch_time_start)

    def on_predict_end(self, batch, logs={}):
        self.training_time.append(time.time() - self.training_time_start)


def generate_data(input_shape_X, N, n_of_class):
    '''
    Teacher definition
    '''
    initializer = tf.keras.initializers.RandomNormal(mean=0., stddev=1.)
    teacher = Sequential()
    teacher.add(Dense(teacher_size, activation='sigmoid',
                      kernel_initializer=initializer,
                      input_shape=(input_shape_X,)))
    teacher.add(Dense(n_of_class,
                      activation='softmax'))
    '''
    Random Data generation
    '''
    data = tf.random.normal((N, input_shape_X), 0, 1)
    labels = teacher.predict(data).argmax(1)
    labels = tf.convert_to_tensor(labels)

    labels = to_categorical(labels, num_classes=n_of_class)
    x_train = data[:int(N*9/10)]
    x_test = data[int(N*9/10):]
    y_train = labels[:int(N*9/10)]
    y_test = labels[int(N*9/10):]
    return (x_train, y_train), (x_test, y_test)


def create_model(input_shape_X):
    model = Sequential()

    if net_size == 0:
        model.add(Dense(n_of_class,
                        activation='softmax',
                        input_shape=(input_shape_X,)))
    else:
        model.add(Dense(net_size, activation='sigmoid', input_shape=(input_shape_X,)))
        model.add(Dense(n_of_class, activation='softmax'))

    loss = keras.losses.CategoricalCrossentropy()
    optim = keras.optimizers.SGD(learning_rate=0.01, momentum=0.05)
    metrics = ["accuracy"]
    model.compile(loss=loss, optimizer=optim, metrics=metrics)

    return model


def training_benchmark(input_shape_X, batch_size, net_size, n_of_class):
    """
    Training benchmark evaluating number of inputs processed per second
    """
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_training"+dt_string+".txt", 'w')

    (X_train, Y_train), (_, _) = generate_data(input_shape_X, N, n_of_class)

    model = create_model(input_shape_X=input_shape_X)

    time_callback = TimeHistory()
    model.fit(X_train, Y_train, epochs=n_epochs_training, batch_size=batch_size,
              callbacks=[time_callback],
              verbose=1)

    training_time = sum(time_callback.batch_times)  # total time
    time_per_epoch = training_time / n_epochs_training
    time_per_batch = time_per_epoch / (len(X_train)//batch_size)  # time per batch
    time_per_sample = time_per_epoch / len(X_train)  # time per sample
    training_sample_per_second = 1./time_per_sample  # sample per seconds

    L = [str(training_time), ',', str(time_per_batch), ',', str(time_per_sample),
         ',', str(training_sample_per_second)]
    stats_file.writelines(L)

    print('TRAINING COMPLETED!')
    stats_file.close()


def inference_benchmark(input_shape_X, batch_size, net_size, n_of_class):
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_inference"+dt_string+".txt", 'w')

    (X_train, Y_train), (X_test, _) = generate_data(input_shape_X, N, n_of_class)

    """
    Training the model without measuring its performances to prepare for inference
    """
    model = create_model(input_shape_X=input_shape_X)

    model.fit(X_train, Y_train, epochs=n_epochs, batch_size=batch_size, verbose=0)

    print('TRAINING COMPLETED!')

    """
    Performing inference on Out-of-Sample multiple times to obtain average performance
    """
    sample_count = 0
    total_time = 0
    keep_running = True

    def handler(foo, bar):
        """
        An handler to catch Ctrl-C for graceful exit
        """
        global keep_running
        keep_running = False

    signal.signal(signal.SIGINT, handler)

    while(keep_running):
        L = []
        for X in X_test:  # online prediction (one sample at time)
            X = np.expand_dims(X, 0)
            start_time = time.time()
            _ = model(X)
            end_time = time.time() - start_time
            total_time += end_time
            sample_count += 1
            latency = total_time/sample_count
            throughput = sample_count/total_time
            L = [str(end_time), ',', str(sample_count), ',', str(
                latency), ',', str(throughput), ',', str(total_time)]
            stats_file.writelines(L)
            stats_file.writelines('\n')

    stats_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML Teacher-Student benchmark")
    parser.add_argument("device_type",
                        choices=["gpu", "cpu"],
                        default="gpu")
    parser.add_argument("mode",
                        choices=["training", "inference"],
                        default="inference")
    parser.add_argument("gpu_index", default=0, nargs='?')
    parser.add_argument("net_size", default=2000, nargs='?')
    parser.add_argument("input_shape_X", default=20000, nargs='?')

    args = parser.parse_args()
    dev = args.device_type
    mode = args.mode
    gpu_index = args.gpu_index
    net_size = args.net_size
    input_shape_X = args.input_shape_X

    """
    SET DEVICE
    """
    if dev == 'cpu':
        de = '/cpu:0'
    elif dev == 'gpu':
        """
        Checking GPU availability
        """
        if tf.config.list_physical_devices('GPU') == 0:
            print("GPU unavailable. Aborting.")
            sys.exit(0)

        """
        Telling to the used GPU to automatically increase the amount of used memory
        """
        GPUs = GPUtil.getGPUs()
        gpus = tf.config.list_physical_devices('GPU')

        if gpus:
            if len(gpus) >= gpu_index+1:
                tf.config.experimental.set_memory_growth(gpus[gpu_index], True)
            else:
                print(f"GPU {gpu_index} not found. Aborting.")
                sys.exit(0)
        else:
            print("No GPU found. Aborting.")
            sys.exit(0)

        de = f'/device:GPU:{gpu_index}'

    with tf.device(de):
        nvidia_smi.nvmlInit()
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(gpu_index)

        if mode == 'training':
            training_benchmark(input_shape_X, batch_size, net_size, n_of_class)
        elif mode == 'inference':
            inference_benchmark(input_shape_X, batch_size, net_size, n_of_class)
