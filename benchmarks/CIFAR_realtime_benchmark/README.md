# CIFAR10 Deep Learning benchmark

## Introduction:

This benchmark implements a convolutional neural network and performs training and inference over the CIFAR10 dataset.
CIFAR10 is a well known image recognition dataset suitable for benchmarking application due to its simple structure and low complexity. The CNN implemented by the benchmark has two convolutional layers and one fully connected layer.
The benchmark aims to measure training and inference performance in terms of total time execution and sample processing time. The resulting values are automatically stored on an output file. 

## Presets:

Through the presets json files it's possible to choose to benchmark inference or training. 
With training mode the benchmark performs only training. Number of epoch for training mode is set to 10, but it's possible to modify this value changing one parameter inside the code. In training mode the benchmark return a single set of statistics related to the total training process.
On the other hands, when inference mode is selected the benchmark performs training for 10 epochs and then do online inference over the whole CIFAR10 test set. Online learning means that the model take only one sample at time, i.e. the batch size is set to one. In this mode only the inference phase is monitored and the benchmark records processing time of each data sample.

## Devices supported:

The device (GPU or CPU) is selected when the benchmark is started from presets. By default every preset choses GPU.

## Dependencies installation

The benchmark dependencies are automatically installed by the benchmark. 

Note that some CUDA libraries require [manual installation](../../README.md#requirements)
