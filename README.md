<h1  align="center">

<img  src="https://i.imgur.com/l4DGFEw.png"  width="224px"/><br/>

<p>OpenForBC-Benchmark</p>

</h1>

**OpenForBC-Benchmark** is a suite of ready-to-run benchmarks that execute in an automated manner along with reporting of test results, detection of installed system software/hardware, and other features.

This standalone tool was developed to benchmark performances of various partitioning options on industrial-grade GPUs, as a part of OpenForBC efforts to develop a framework capable of presenting a common interface on top of GPUs to overcome the barriers introduced by payware environments such as VMware ESXi and CITRIX and providing extended support for Linux KVM, more of which can be found [here](https://hackmd.io/@gfronze/r1j6FIb9U).

The framework is compatible with Windows, Linux, and macOS given the benchmark supports the tester operating system.
___

## Requirements

- Python 3.6 minimum
- pip 10.0 minimum (can be updated by running `pip3 install -U pip`)

## Installation 

- Clone the repository

```bash
git clone --recursive https://github.com/Open-ForBC/OpenForBC-Benchmark.git
```

- Install the `o4bc-bench` tool

```bash
cd OpenForBC-Benchmark
pip3 install .
```

___

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



## [Licenses](LICENSE)
