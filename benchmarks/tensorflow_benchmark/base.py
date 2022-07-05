# Copyright (c) 2021-2022 Istituto Nazionale di Fisica Nucleare
# SPDX-License-Identifier: MIT

from argparse import ArgumentParser
from time import perf_counter

from tensorflow.keras.callbacks import Callback


class Benchmark:
    def __init__(self, name: str):
        from sys import exit

        from tensorflow.config import list_physical_devices
        from tensorflow.config.experimental import set_memory_growth

        self.name = name

        parser = ArgumentParser(description="A ML MNIST benchmark")
        parser.add_argument("device_type", choices=["gpu", "cpu"], default="gpu")
        parser.add_argument(
            "mode", choices=["training", "inference", "test"], default="inference"
        )
        parser.add_argument("-g", "--gpu_index", default=0, nargs="?")
        parser.add_argument(
            "-n", "--n_epochs_training", default=50, nargs="?", type=int
        )
        parser.add_argument("-bs", "--batch_size", default=32, nargs="?", type=int)
        parser.add_argument(
            "-l",
            "--iteration_limit",
            help="Maximum number of inference iterations",
            type=int,
        )

        args = parser.parse_args()
        dev_type = args.device_type
        self.mode = args.mode
        gpu_index = args.gpu_index
        self.n_epochs_training = args.n_epochs_training
        self.batch_size = args.batch_size
        self.iteration_limit = args.iteration_limit

        # SET DEVICE
        if dev_type == "cpu":
            self.dev = "/cpu:0"
        elif dev_type == "gpu":
            # Check GPU availability
            if list_physical_devices("GPU") == 0:
                print("GPU unavailable. Aborting.")
                exit(0)

            gpus = list_physical_devices("GPU")

            if gpus:
                if len(gpus) >= gpu_index + 1:
                    # Use dynamic GPU memory allocation
                    set_memory_growth(gpus[gpu_index], True)
                else:
                    print(f"GPU {gpu_index} not found. Aborting.")
                    exit(0)
            else:
                print("No GPU found. Aborting.")
                exit(0)

            self.dev = f"/device:GPU:{gpu_index}"

    @staticmethod
    def gen_stats_file_name(prefix):
        """Generate stats file name with prefix."""
        from time import strftime

        return f'stats_{prefix}_{strftime("%Y-%m-%d_%H-%M-%S")}.txt'

    def set_data(self, X, Y):
        self.X = X
        self.Y = Y

    def set_model(self, model):
        self.model = model

    def run(self):
        from tensorflow import device

        if self.mode == "test":
            print("total_time: 0.0\navg_time_per_sample: 0.0")
            exit(0)

        with device(self.dev):
            if self.mode == "training":
                self.training_benchmark()
            elif self.mode == "inference":
                self.inference_benchmark()

    def training_benchmark(self):
        """
        Perform training benchmark.

        Evaluates number of training inputs processed per second.
        """
        time_callback = TimeHistory()
        self.model.fit(
            self.X,
            self.Y,
            epochs=self.n_epochs_training,
            batch_size=self.batch_size,
            verbose=1,
            callbacks=[time_callback],
        )

        with open(
            Benchmark.gen_stats_file_name(f"{self.name}-training"), "w"
        ) as stats_file:
            for batch_time in time_callback.batch_times:
                stats_file.write(f"{batch_time}\n")

        print("TRAINING COMPLETED!")

        total_time = sum(time_callback.batch_times)

        print(
            f"total_time: {total_time}\n"
            "avg_time_per_sample: "
            + f"{total_time / self.n_epochs_training / self.X.shape[0]}"
        )

    def inference_benchmark(self):
        """
        Perform inference benchmark.

        Evaluates number of Out-of-Sample inputs processed per second.
        """
        from math import ceil

        # Perform inference on Out-of-Sample multiple times to obtain average performance
        n_iterations = 0
        total_time = 0.0
        keep_running = True
        with open(
            Benchmark.gen_stats_file_name(f"{self.name}-inference"), "w"
        ) as stats_file:
            while keep_running:
                print(f"Iteration {n_iterations}")
                try:
                    for i in range(ceil(len(self.X) / self.batch_size)):
                        pos = i * self.batch_size
                        x = self.X[pos : pos + self.batch_size]
                        start_time = perf_counter()
                        _ = self.model(x)
                        batch_time = perf_counter() - start_time
                        total_time += batch_time
                        stats_file.write(f"{batch_time / len(x)}\n")
                        stats_file.flush()
                except KeyboardInterrupt:
                    keep_running = False
                    break
                n_iterations += 1
                if self.iteration_limit and n_iterations + 1 > self.iteration_limit:
                    break

        print("INFERENCE COMPLETED!")
        print(
            f"total_time: {total_time}\n"
            f"avg_time_per_sample: {total_time / (len(self.X) * n_iterations)}"
        )


class TimeHistory(Callback):
    """A set of custom Keras callbacks to monitor Nvidia GPUs compute time."""

    def on_train_begin(self, logs={}):
        self.batch_times = []
        self.epoch_times = []
        self.training_time = []
        self.training_time_start = perf_counter()

    def on_predict_begin(self, logs={}):
        self.batch_times = []
        self.epoch_times = []
        self.training_time = []
        self.training_time_start = perf_counter()

    def on_train_batch_begin(self, batch, logs={}):
        self.batch_time_start = perf_counter()

    def on_train_batch_end(self, batch, logs={}):
        self.batch_times.append(perf_counter() - self.batch_time_start)

    def on_train_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = perf_counter()

    def on_train_epoch_end(self, batch, logs={}):
        self.epoch_times.append(perf_counter() - self.epoch_time_start)

    def on_train_end(self, batch, logs={}):
        self.training_time.append(perf_counter() - self.training_time_start)

    def on_predict_batch_begin(self, batch, logs={}):
        self.batch_time_start = perf_counter()

    def on_predict_batch_end(self, batch, logs={}):
        self.batch_times.append(perf_counter() - self.batch_time_start)

    def on_predict_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = perf_counter()

    def on_predict_epoch_end(self, batch, logs={}):
        self.epoch_times.append(perf_counter() - self.epoch_time_start)

    def on_predict_end(self, batch, logs={}):
        self.training_time.append(perf_counter() - self.training_time_start)
