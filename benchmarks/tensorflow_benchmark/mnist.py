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

from base import Benchmark

import tensorflow.keras as keras

# Global variables definition
batch_size = 1
n_epochs = 6
n_epochs_training = 50
n_of_class = 10
N = 150
teacher_size = 8


def load_MNIST_data():
    """Load and reshape the standard MNIST dataset."""
    from keras.datasets import mnist

    (x, y), _ = mnist.load_data()

    return x / 255.0, y


def create_MNIST_model():
    model = keras.models.Sequential(
        [
            keras.layers.Flatten(input_shape=(28, 28)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(0.001),
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[keras.metrics.SparseCategoricalAccuracy()],
    )

    return model


if __name__ == "__main__":
    bench = Benchmark("MNIST")
    bench.set_data(*load_MNIST_data())
    bench.set_model(create_MNIST_model())
    bench.run()
