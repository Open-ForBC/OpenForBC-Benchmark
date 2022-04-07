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
import argparse

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
    Estimate recall.

    recall = TP / (TP + FN)
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def precision_m(y_true, y_pred):
    """
    Estimate precision.

    precision = TP / (TP + FP)
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def f1(y_true, y_pred):
    """
    F1 score in tensorflow.

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
    """Create a tf.keras.Sequential() model."""
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


def gen_stats_file_name(prefix):
    """Generate stats file name with prefix."""
    from time import strftime

    return f'stats_file_{prefix}_{strftime("%Y-%m-%d_%H-%M-%S")}.txt'


def training_benchmark(batch_size):
    """
    Perform training benchmark.

    Evaluates number of training inputs processed per second.
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
    time_callback = TimeHistory()
    model.fit(
        X,
        Y,
        epochs=n_epochs_training,
        batch_size=batch_size,
        verbose=1,
        callbacks=[time_callback],
    )

    with open(gen_stats_file_name("training"), "w") as stats_file:
        for batch_time in time_callback.batch_times:
            stats_file.write(f"{batch_time}\n")

    print("TRAINING COMPLETED!")

    total_time = sum(time_callback.batch_times)

    print(
        f"total_time: {total_time}\n"
        f"avg_time_per_sample: {total_time / n_epochs_training / X.shape[0]}"
    )


def inference_benchmark(iteration_limit=None):
    """
    Perform inference benchmark.

    Evaluates number of Out-of-Sample inputs processed per second.
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

    # Perform inference on Out-of-Sample multiple times to obtain average performance
    n_iterations = 0
    total_time = 0.0
    keep_running = True
    with open(gen_stats_file_name("inference"), "w") as stats_file:
        while keep_running:
            print(f"Iteration {n_iterations}")
            try:
                for x in X:
                    x = x.reshape(1, -1)
                    start_time = time.time()
                    _ = model(x)
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
        f"avg_time_per_sample: {total_time / (len(X) * n_iterations)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A ML MNIST benchmark")
    parser.add_argument("device_type", choices=["gpu", "cpu"], default="gpu")
    parser.add_argument(
        "mode", choices=["training", "inference", "test"], default="inference"
    )
    parser.add_argument("-g", "--gpu_index", default=0, nargs="?")
    parser.add_argument("-n", "--n_epochs_training", default=50, nargs="?", type=int)
    parser.add_argument("-bs", "--batch_size", default=32, nargs="?", type=int)
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
            training_benchmark(batch_size)
        elif mode == "inference":
            inference_benchmark(iteration_limit=args.iteration_limit)
        elif mode == "test":
            print("total_time: 0.0\navg_time_per_sample: 0.0")
