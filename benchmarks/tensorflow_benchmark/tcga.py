#!/usr/bin/env python
# File created in 2022 by Filippo Valle
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import backend as K
import numpy as np

from base import Benchmark


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


if __name__ == "__main__":
    bench = Benchmark("TCGA")

    bench.set_data(*preprocess_data(True))

    bench.set_model(
        create_model(
            SGD(0.001, momentum=0.99),
            l1=0.0001,
            l2=0.0001,
            hidden=50,
            input_dim=bench.X.shape[1],
            output_dim=bench.Y.shape[1],
            loss=categorical_crossentropy,
            activation_func="softmax",
            verbose=True,
        )
    )

    bench.run()
