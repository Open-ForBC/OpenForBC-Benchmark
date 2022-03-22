# MNIST Deep Learning benchmark

## Introduction:

This benchmark implements a fully connected neural network and performs training and inference over the MNIST dataset.
MNIST is a well known image recognition dataset suitable for benchmarking application due to its simple structure and low complexity. The FCNN implemented by the benchamrk has three fully connected layers.
The benchamrk aims to measure training and inference performance in terms of total time execution and sample processing time. The resulting values are automatically stored on an output file. 

## Presets:

Through the presets json files it's possible to choose to benchmark inference or training. 
With training mode the benchmark performs only training. Number of epoch for training mode is set to 50, but it's possible to modify this value changing one parameter inside the code. In training mode the benchmark return a single set of statistics related to the total training process.
On the other hands, when inference mode is selected the benchmark performs training for 6 epochs and then do online inference over the whole MNIST test set. Online learning means that the model take only one sample at time, i.e. the batch size is set to one. In this mode only the inference phase is monitored and the benchamrk records processing time of each data sample.

## Devices supported:

The device (GPU or CPU) is selected when the benchmark is started from presets. By defalut every preset choses GPU.

## Dependencies installation

The benchmark dependencies are automatically installed by the benchmark. 