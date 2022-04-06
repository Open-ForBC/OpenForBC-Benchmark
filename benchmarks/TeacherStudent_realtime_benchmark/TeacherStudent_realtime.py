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
import argparse

import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from keras.utils.np_utils import to_categorical


# Global variables definition
batch_size = 1
n_epochs = 1
n_epochs_training = 200
n_of_class = 10
N = 150
teacher_size = 8


class TimeHistory(keras.callbacks.Callback):
    """A set of custom Keras callbacks to monitor Nvidia GPUs compute time."""

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
    # Teacher definition
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
    x_train = data[: int(N * 9 / 10)]
    x_test = data[int(N * 9 / 10) :]
    y_train = labels[: int(N * 9 / 10)]
    y_test = labels[int(N * 9 / 10) :]
    return (x_train, y_train), (x_test, y_test)


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


def gen_stats_file_name(prefix):
    """Generate stats file name with prefix."""
    from time import strftime

    return f'stats_file_{prefix}_{strftime("%Y-%m-%d_%H-%M-%S")}.txt'


def training_benchmark(input_shape_X, batch_size, n_of_class):
    """
    Perform training benchmark.

    Evaluates number of training inputs processed per second.
    """
    (X_train, Y_train), (_, _) = generate_data(input_shape_X, N, n_of_class)
    model = create_model(input_shape_X=input_shape_X)

    time_callback = TimeHistory()
    model.fit(
        X_train,
        Y_train,
        epochs=n_epochs_training,
        batch_size=batch_size,
        callbacks=[time_callback],
        verbose=1,
    )

    with open(gen_stats_file_name("training"), "w") as stats_file:
        for batch_time in time_callback.batch_times:
            stats_file.write(f"{batch_time}\n")

    print("TRAINING COMPLETED!")

    total_time = sum(time_callback.batch_times)

    print(
        f"total_time: {total_time}\n"
        f"avg_time_per_sample: {total_time / n_epochs_training / len(X_train)}"
    )


def inference_benchmark(input_shape_X, batch_size, n_of_class, iteration_limit=None):
    """
    Perform inference benchmark.

    Evaluates number of Out-of-Sample inputs processed per second.
    """
    (X_train, Y_train), (X_test, _) = generate_data(input_shape_X, N, n_of_class)
    model = create_model(input_shape_X=input_shape_X)

    # Train the model without measuring its performance to prepare for inference
    model.fit(X_train, Y_train, epochs=n_epochs, batch_size=batch_size, verbose=0)
    print("TRAINING COMPLETED!")

    # Perform inference on Out-of-Sample multiple times to obtain average performance
    n_iterations = 0
    total_time = 0.0
    keep_running = True
    with open(gen_stats_file_name("inference"), "w") as stats_file:
        while keep_running:
            print(f"Iteration {n_iterations}")
            try:
                for X in X_test:
                    X = np.expand_dims(X, 0)
                    start_time = time.time()
                    _ = model(X)
                    sample_time = time.time() - start_time
                    total_time += sample_time
                    stats_file.write(f"{sample_time}\n")
                    stats_file.flush()
            except KeyboardInterrupt:
                keep_running = False
                break
            n_iterations += 1
            if iteration_limit and n_iterations + 1 > iteration_limit:
                break

    print("INFERENCE COMPLETED!")
    print(
        f"total_time: {total_time}\n"
        f"avg_time_per_sample: {total_time / (len(X_test) * n_iterations)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML Teacher-Student benchmark")
    parser.add_argument("device_type", choices=["gpu", "cpu"], default="gpu")
    parser.add_argument(
        "mode", choices=["training", "inference", "test"], default="inference"
    )
    parser.add_argument("-g", "--gpu_index", default=0, nargs="?")
    parser.add_argument("-s", "--net_size", default=2000, nargs="?")
    parser.add_argument("-n", "--n_epochs_training", default=200, nargs="?", type=int)
    parser.add_argument("-i", "--input_shape_X", default=20000, nargs="?")
    parser.add_argument("-t", "--test_mode", action="store_true")
    parser.add_argument(
        "-l",
        "--iteration_limit",
        help="Maximum number of inference iterations",
        type=int,
    )

    args = parser.parse_args()
    dev = args.device_type
    mode = args.mode
    gpu_index = args.gpu_index
    net_size = args.net_size
    input_shape_X = args.input_shape_X
    n_epochs_training = args.n_epochs_training

    # SET DEVICE
    if dev == "cpu":
        de = "/cpu:0"
    elif dev == "gpu":
        # Check GPU availability
        if tf.config.list_physical_devices("GPU") == 0:
            print("GPU unavailable. Aborting.")
            sys.exit(0)

        gpus = tf.config.list_physical_devices("GPU")

        if gpus:
            if len(gpus) >= gpu_index + 1:
                # Use dynamic GPU memory allocation
                tf.config.experimental.set_memory_growth(gpus[gpu_index], True)
            else:
                print(f"GPU {gpu_index} not found. Aborting.")
                sys.exit(0)
        else:
            print("No GPU found. Aborting.")
            sys.exit(0)

        de = f"/device:GPU:{gpu_index}"

    with tf.device(de):
        if mode == "training":
            training_benchmark(input_shape_X, batch_size, n_of_class)
        elif mode == "inference":
            inference_benchmark(
                input_shape_X,
                batch_size,
                n_of_class,
                iteration_limit=args.iteration_limit,
            )
        elif mode == "test":
            print("total_time: 0.0\navg_time_per_sample: 0.0")
