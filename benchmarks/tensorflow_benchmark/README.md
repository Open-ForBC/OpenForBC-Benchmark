# OpenForBC Tensorflow benchmark

## Description

This benchmark is a collection of machine learning benchmarks all based on
Tensorflow.

Every benchmark measures the average time per sample for each operation mode.

Benchmarks can run in either training or inference mode: there are multiple
presets for each benchmark.

## Requirements

Tensorflow requires NVIDIA CUDNN and some CUDA libraries to run, specifically:

- `cudart`
- `libcublas`
- `libcufft`
- `libcurand`
- `libcusolver`
- `libcusparse`
  
## Benchmark list

- [MNIST Real Time Benchmarking](doc/MNIST)
- [CIFAR10 Real Time Benchmarking](doc/CIFAR)
- [Teacher-Student Real Time Benchmarking](doc/TeacherStudent)
- [TCGA topic modeling benchmark](doc/TCGA)

