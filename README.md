<h1  align="center">

<img  src="https://i.imgur.com/l4DGFEw.png"  width="224px"/><br/>

<p>OpenForBC-Benchmark</p>

</h1>

**OpenForBC-Benchmark** is a suite of ready-to-run benchmarks that execute in an automated manner along with reporting of test results, detection of installed system software/hardware, and other features.

This standalone tool was developed to benchmark performances of various partitioning options on industrial-grade GPUs, as a part of OpenForBC efforts to develop a framework capable of presenting a common interface on top of GPUs to overcome the barriers introduced by payware environments such as VMware ESXi and CITRIX and providing extended support for Linux KVM, more of which can be found [here](https://hackmd.io/@gfronze/r1j6FIb9U).

The framework is compatible with Windows, Linux, and macOS given the benchmark supports the tester operating system.
___

## Requirements

-   Python: >= 3.9
-   pip: >= 10.0 (can be updated by running `pip3 install -U pip`)

ML benchmarks depends on tensorflow, which requires NVIDIA CUDNN and some cuda
libraries to be installed, specifically:

-   cuda-cudart
-   libcublas
-   libcufft
-   libcurand
-   libcusolver
-   libcusparse

Please refer to [TensorFlow's guide for GPU
support](https://www.tensorflow.org/install/gpu#linux_setup) if you are using
ubuntu or to NVIDIA's documentation for [CUDNN
installation](https://developer.nvidia.com/cudnn) and [CUDA toolkit
installation](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html).

## Documentation

- Guide to developer [docs](docs/developer-guide.md).

- Guide to user [docs](docs/user-guide.md).

## Benchmarks

Currently, the following benchmarks are implemented:

- [Dummy](benchmarks/dummy_benchmark).
- [Blender](benchmarks/blender_benchmark).
- [Matmul](benchmarks/matmul_benchmark)
- [MatmulC++](benchmarks/matmulCpp_benchmark)
- [MNIST Real Time Benchmarking](benchmarks/MNIST_realtime_benchmark)
- [CIFAR10 Real Time Benchmarking](benchmarks/CIFAR_realtime_benchmark)
- [Teacher-Student Real Time Benchmarking](benchmarks/TeacherStudent_realtime_benchmark)
- [MNIST FCNN](benchmarks/MNIST_FCNeuralNetwork)
- [TCGA_topicmodeling](benchmarks/TCGA_topicmodeling)



## [Licenses](LICENSE)
