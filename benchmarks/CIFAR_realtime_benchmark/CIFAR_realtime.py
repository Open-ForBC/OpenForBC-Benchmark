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
from datetime import datetime
import argparse
import signal
try:
    import nvidia_smi
except ModuleNotFoundError:
    print("nvidia-smi has not been found. GPU support is excluded.")
    pass
import GPUtil
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np


"""
Global variables definition
"""
batch_size = 1
n_epochs = 10
n_epochs_training = 10
n_of_class = 10
N = 150
teacher_size = 8
gpu_performance_sampling_time = 1
keep_running = True


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


def load_CIFAR_data():
    """
    Loading and shaping the standard CIFAR dataset
    """
    (train_images, train_labels), (test_images,
                                   test_labels) = keras.datasets.cifar10.load_data()

    # Normalize pixel values to be between 0 and 1
    train_images, test_images = train_images / 255.0, test_images / 255.0

    return (train_images, train_labels), (test_images, test_labels)


def create_CIFAR_model():
    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(32, (3, 3), activation='relu',
                                  input_shape=(32, 32, 3)))
    model.add(keras.layers.MaxPooling2D((2, 2)))
    model.add(keras.layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(keras.layers.MaxPooling2D((2, 2)))
    model.add(keras.layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(10))
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    return model


def training_benchmark(batch_size):
    """
    Training benchmark evaluating number of training inputs processed per second
    """
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_training"+dt_string+".txt", 'w')

    (train_images, train_labels), (_, _) = load_CIFAR_data()

    model = create_CIFAR_model()

    time_callback = TimeHistory()
    model.fit(train_images, train_labels,
              epochs=n_epochs_training,
              callbacks=[time_callback],
              batch_size=batch_size,
              verbose=1)

    training_time = sum(time_callback.batch_times)  # total time
    time_per_epoch = training_time / n_epochs_training
    time_per_batch = time_per_epoch / (len(train_images)//batch_size)  # time per batch
    time_per_sample = time_per_epoch / len(train_images)  # time per sample
    training_sample_per_second = 1./time_per_sample  # sample per seconds

    L = [str(training_time), ',', str(time_per_batch), ',', str(time_per_sample),
         ',', str(training_sample_per_second)]
    stats_file.writelines(L)

    print('TRAINING COMPLETED!')
    stats_file.close()


def inference_benchmark(iteration_limit=None):
    """
    Inference benchmark evaluating number of Out-of-Sample inputs processed per second
    """
    global keep_running
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_inference"+dt_string+".txt", 'w')

    (train_images, train_labels), (test_images, _) = load_CIFAR_data()

    """
    Training the model without measuring its performances to prepare for inference
    """
    model = create_CIFAR_model()

    model.fit(train_images, train_labels, epochs=n_epochs, verbose=0)

    print('TRAINING COMPLETED!')

    """
    Performing inference on Out-of-Sample multiple times to obtain average performance
    """
    sample_count = 0
    total_time = 0

    n_iterations = 0

    while(keep_running):
        print(f"Iteration {n_iterations}")
        L = []
        for IMG in test_images:  # online prediction (one sample at time)
            try:
                IMG = np.expand_dims(IMG, 0)
                start_time = time.time()
                _ = model(IMG)
                end_time = time.time() - start_time
                total_time += end_time
                sample_count += 1
                latency = total_time/sample_count
                throughput = sample_count/total_time
                L = [str(end_time), ',', str(sample_count), ',', str(
                    latency), ',', str(throughput), ',', str(total_time)]
                stats_file.writelines(L)
                stats_file.writelines('\n')
            except KeyboardInterrupt:
                keep_running = False
                break
        n_iterations += 1
        if iteration_limit:
            if n_iterations+1 > iteration_limit:
                break

    print('INFERENCE COMPLETED!')
    stats_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML CIFAR benchmark")
    parser.add_argument("device_type",
                        choices=["gpu", "cpu"],
                        default="gpu")
    parser.add_argument("mode",
                        choices=["training", "inference"],
                        default="inference")
    parser.add_argument("-g", "--gpu_index", default=0, nargs='?')
    parser.add_argument("-n", "--n_epochs_training", default=50, nargs='?', type=int)
    parser.add_argument("-t", "--test_mode", action='store_true')
    parser.add_argument("-l", "--iteration_limit",
                        help="Maximum number of inference iterations", type=int)

    args = parser.parse_args()
    dev = args.device_type
    mode = args.mode
    gpu_index = args.gpu_index
    n_epochs_training = args.n_epochs_training

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
        if dev == 'gpu':
            nvidia_smi.nvmlInit()
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(gpu_index)

        if mode == 'training':
            training_benchmark(batch_size)
        elif mode == 'inference':
            inference_benchmark(iteration_limit=args.iteration_limit)

        if args.test_mode:
            print("Training GPU usage: 0")
            print("Training GPU memory usage: 0")
            print("Training Time: 0")
            print("Training sample processing speed: 0")
            print("In-sample inference GPU usage: 0")
            print("In-sample inference GPU memory usage: 0")
            print("In-sample inference time: 0")
            print("In-sample sample processing speed: 0")
            print("Out-of-Sample inference GPU usage: 0")
            print("Out-of-Sample inference GPU memory usage: 0")
            print("Out-of-Sample inference time: 0")
            print("Out-of-Sample sample processing speed: 0")
