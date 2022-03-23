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
import tensorflow_datasets as tfds
import tensorflow.keras as keras
import numpy as np

"""
Global variables definition
"""
batch_size = 1
n_epochs = 6
n_epochs_training = 50
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


def load_MNIST_data():
    """
    Loading and shaping the standard MNIST dataset
    """
    (ds_train, ds_test), ds_info = tfds.load(
        'mnist',
        split=['train', 'test'],
        shuffle_files=True,
        as_supervised=True,
        with_info=True,
    )

    def normalize_img(image, label):
        """Normalizes images: `uint8` -> `float32`."""
        return tf.cast(image, tf.float32) / 255., label

    ds_train = ds_train.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_train = ds_train.cache()
    ds_train = ds_train.shuffle(ds_info.splits['train'].num_examples)
    ds_train = ds_train.batch(128)
    ds_train = ds_train.prefetch(tf.data.AUTOTUNE)

    ds_test = ds_test.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_test = ds_test.batch(128)
    ds_test = ds_test.cache()
    ds_test = ds_test.prefetch(tf.data.AUTOTUNE)

    return ds_train, ds_test


def create_MNIST_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )

    return model


def training_benchmark(batch_size):
    """
    Training benchmark evaluating number of training inputs processed per second
    """
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_training"+dt_string+".txt", 'w')

    ds_train, _ = load_MNIST_data()

    model = create_MNIST_model()

    time_callback = TimeHistory()
    model.fit(ds_train,
              epochs=n_epochs_training,
              callbacks=[time_callback],
              batch_size=batch_size,
              verbose=1)

    training_time = sum(time_callback.batch_times)  # total time
    time_per_epoch = training_time / n_epochs_training
    time_per_batch = time_per_epoch / (len(ds_train)//batch_size)  # time per batch
    time_per_sample = time_per_epoch / len(ds_train)  # time per sample
    training_sample_per_second = 1./time_per_sample  # sample per seconds

    L = [str(training_time), ',', str(time_per_batch), ',', str(time_per_sample),
         ',', str(training_sample_per_second)]
    stats_file.writelines(L)

    print('TRAINING COMPLETED!')
    stats_file.close()


def inference_benchmark():
    """
    Inference benchmark evaluating number of Out-of-Sample inputs processed per second
    """
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_inference"+dt_string+".txt", 'w')

    ds_train, ds_test = load_MNIST_data()

    """
    Training the model without measuring its performances to prepare for inference
    """
    model = create_MNIST_model()

    model.fit(ds_train, epochs=n_epochs, verbose=0)

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
        for batch in ds_test:  # online prediction (one sample at time)
            for DS in batch[0]:
                DS = np.expand_dims(DS, 0)
                start_time = time.time()
                _ = model(DS)
                end_time = time.time() - start_time
                total_time += end_time
                sample_count += 1
                latency = total_time/sample_count
                throughput = sample_count/total_time
                L = [str(end_time), ',', str(sample_count), ',', str(
                    latency), ',', str(throughput), ',', str(total_time)]
                stats_file.writelines(L)
                stats_file.writelines('\n')

    print('INFERENCE COMPLETED!')
    stats_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML MNIST benchmark")
    parser.add_argument("device_type",
                        choices=["gpu", "cpu"],
                        default="gpu")
    parser.add_argument("mode",
                        choices=["training", "inference"],
                        default="inference")
    parser.add_argument("-g", "--gpu_index", default=0, nargs='?')
    parser.add_argument("-n", "--n_epochs_training", default=50, nargs='?', type=int)

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
            inference_benchmark()
