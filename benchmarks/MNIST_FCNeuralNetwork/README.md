# MNIST classification benchmark with fully connected neural network

## Introduction:

This benchmark implements a fully connected neural network and perform training and inference over MNIST dataset. 

## Presets:

Through the presets json files it's possible to choose neural network architecture, batch size during training (how many data I give to the net per training iteration) and device used by the benchmark (GPU or CPU). By now only shallow network with 1000 neurons is available, while is possible to choose between small batch size (64 sample) and large batch size (1024).

## Devices supported:

The device (GPU or CPU) is selected through presets.

## Dependencies installation

The benchmark dependencies are automatically installed by the benchmark. 