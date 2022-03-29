#!/usr/bin/env python
# File created in 2022 by Filippo Valle
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
import sys
from datetime import datetime
import argparse

try:
    import nvidia_smi
except ModuleNotFoundError:
    print("nvidia-smi has not been found. GPU support is excluded.")
    pass
import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import backend as K
import numpy as np

"""
Global variables definition
"""
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


def preprocess_data(
    verbose=True,
    L=0,
    algorithm="topsbm",
    directory="breast",
    label="Subtype_Selected_Lum",
):
    # get the reduced space matrix
    filename = f"{directory}/{algorithm}/{algorithm}_level_{L}_topic-dist.csv"
    df_topics = pd.read_csv(filename)
    df_topics = df_topics.set_index("doc").drop("i_doc", axis=1)
    filename = "%s/%s/%s_level_%d_word-dist.csv" % (directory, algorithm, algorithm, L)
    df_words = pd.read_csv(filename, index_col=0)

    # clean gene ENSG names
    df_words.index = [g[:15] for g in df_words.index]

    # read original space data and normalise
    filename = "%s/mainTable.csv" % (directory)
    df = pd.read_csv(filename, index_col=0).reindex(index=df_words.index)
    df = df.divide(df.sum(0), 1).transpose().fillna(0)
    df_files = pd.read_csv("%s/files.dat" % (directory), index_col=0)

    # get the tumour subtype (tissue) label
    df_topics.insert(0, "tissue", df_files.reindex(index=df_topics.index)[label])
    df_topics = df_topics[df_topics["tissue"] != "unknown"]
    df_labels = df_files.copy()
    df_labels = df_labels.reindex(index=df_topics.index)
    X = df_topics.drop("tissue", 1)

    # feature scaling to use SGD
    X = (
        X.subtract(X.mean(0), 1)
        .divide(0.5 * (X.max(0) - X.min(0)), 1)
        .values.astype(float)
    )  # SGD transform
    Y = to_categorical(np.unique(df_labels[label], return_inverse=True)[1])

    if verbose:
        print(X.shape, Y.shape)

    return X, Y


def recall_m(y_true, y_pred):
    """
    Estimate recall
    recall = TP / (TP + FN)
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def precision_m(y_true, y_pred):
    """
    Estimate precision
    precision = TP / (TP + FP)
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def f1(y_true, y_pred):
    """
    F1 score in tensorflow
     f1 is the harmonic average of precision and recall
    """
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2 * ((precision * recall) / (precision + recall + K.epsilon()))


def create_model(
    opt,
    l1,
    l2,
    hidden,
    input_dim,
    output_dim,
    loss=categorical_crossentropy,
    activation_func="softmax",
    verbose=True,
):
    """
    Creates a tf.keras.Sequential() model
    """
    K.clear_session()

    model = Sequential()
    model.add(
        Dense(
            units=hidden,
            input_dim=input_dim,
            use_bias=True,
            bias_initializer="ones",
            activation="relu",
            kernel_regularizer=l1_l2(l1=l1, l2=l2),
        )
    )
    model.add(Dense(units=output_dim, activation=activation_func))
    model.compile(loss=loss, optimizer=opt, metrics=["accuracy", "AUC", f1])

    if verbose:
        print(model.summary())
    return model


def training_benchmark(batch_size):
    """
    Training benchmark evaluating number of training inputs processed per second
    """
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_training" + dt_string + ".txt", "w")

    X, Y = preprocess_data(True)

    # L=0 Lum
    model = create_model(
        SGD(0.001, momentum=0.99),
        l1=0.0001,
        l2=0.0001,
        hidden=50,
        input_dim=X.shape[1],
        output_dim=Y.shape[1],
        loss=categorical_crossentropy,
        activation_func="softmax",
        verbose=True,
    )
    time_callback = TimeHistory()
    model.fit(
        X,
        Y,
        epochs=n_epochs_training,
        batch_size=batch_size,
        verbose=1,
        callbacks=[time_callback],
    )

    training_time = sum(time_callback.batch_times)  # total time
    time_per_epoch = training_time / n_epochs_training
    time_per_batch = time_per_epoch / (X.shape[0] / batch_size)  # time per batch
    time_per_sample = time_per_epoch / X.shape[0]  # time per sample
    training_sample_per_second = 1.0 / time_per_sample  # sample per seconds

    L = [
        str(training_time),
        ",",
        str(time_per_batch),
        ",",
        str(time_per_sample),
        ",",
        str(training_sample_per_second),
    ]
    stats_file.writelines(L)

    print("TRAINING COMPLETED!")
    stats_file.close()


def inference_benchmark(iteration_limit=None):
    """
    Inference benchmark evaluating number of Out-of-Sample inputs processed per second
    """
    global keep_running
    dt_string = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    stats_file = open("stats_file_inference" + dt_string + ".txt", "w")

    """
    Training the model without measuring its performances to prepare for inference
    """
    X, Y = preprocess_data(True)

    # L=0 Lum
    model = create_model(
        SGD(0.001, momentum=0.99),
        l1=0.0001,
        l2=0.0001,
        hidden=50,
        input_dim=X.shape[1],
        output_dim=Y.shape[1],
        loss=categorical_crossentropy,
        activation_func="softmax",
        verbose=True,
    )
    print("TRAINING COMPLETED!")

    """
    Performing inference on Out-of-Sample multiple times to obtain average performance
    """
    sample_count = 0
    total_time = 0

    n_iterations = 0

    while keep_running:
        print(f"Iteration {n_iterations}")
        L = []
        for x_batch in X:  # online prediction (one sample at time)
            try:
                _xbatch = x_batch.reshape(1, -1)
                start_time = time.time()
                _ = model(_xbatch)
                end_time = time.time() - start_time
                total_time += end_time
                sample_count += 1
                latency = total_time / sample_count
                throughput = sample_count / total_time
                L = [
                    str(end_time),
                    ",",
                    str(sample_count),
                    ",",
                    str(latency),
                    ",",
                    str(throughput),
                    ",",
                    str(total_time),
                ]
                stats_file.writelines(L)
                stats_file.writelines("\n")
            except KeyboardInterrupt:
                keep_running = False
                break
        n_iterations += 1
        if iteration_limit:
            if n_iterations + 1 > iteration_limit:
                break

    print("INFERENCE COMPLETED!")
    stats_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML MNIST benchmark")
    parser.add_argument("device_type", choices=["gpu", "cpu"], default="gpu")
    parser.add_argument("mode", choices=["training", "inference"], default="inference")
    parser.add_argument("-g", "--gpu_index", default=0, nargs="?")
    parser.add_argument("-n", "--n_epochs_training", default=50, nargs="?", type=int)
    parser.add_argument("-bs", "--batch_size", default=32, nargs="?", type=int)
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
    n_epochs_training = args.n_epochs_training
    batch_size = args.batch_size

    """
    SET DEVICE
    """
    if dev == "cpu":
        de = "/cpu:0"
    elif dev == "gpu":
        """
        Checking GPU availability
        """
        if tf.config.list_physical_devices("GPU") == 0:
            print("GPU unavailable. Aborting.")
            sys.exit(0)

        """
        Telling to the used GPU to automatically increase the amount of used memory
        """
        gpus = tf.config.list_physical_devices("GPU")

        if gpus:
            if len(gpus) >= gpu_index + 1:
                tf.config.experimental.set_memory_growth(gpus[gpu_index], True)
            else:
                print(f"GPU {gpu_index} not found. Aborting.")
                sys.exit(0)
        else:
            print("No GPU found. Aborting.")
            sys.exit(0)

        de = f"/device:GPU:{gpu_index}"

    with tf.device(de):
        if dev == "gpu":
            nvidia_smi.nvmlInit()
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(gpu_index)

        if mode == "training":
            training_benchmark(batch_size)
        elif mode == "inference":
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
