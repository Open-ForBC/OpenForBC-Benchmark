<h1  align="center">

<img  src="https://i.imgur.com/l4DGFEw.png"  style="width: 25vw"/><br/>

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
<div align="center">

| <center>User guide</center> | <center>Developer guide</center> |
| -------- | -------- |
| [<img src="https://i.ibb.co/HT8zDtt/kisspng-crowd-drawing-cartoon-community-5abe5e8dc735f1-335904791522425485816.png" alt="drawing" style="width:20vmin;"/>](docs/user-guide.md) | [<img src="https://i.ibb.co/ZNQx6nw/kisspng-computer-icons-computer-code-vector-graphics-compu-plist-2-json-macappstoreda-5d0f29f75636f9.png" alt="drawing" style="width:20vmin;"/>](docs/developer-guide.md) |

</div>




## Benchmarks

Currently, the following benchmarks are implemented:

- [Dummy](benchmarks/dummy_benchmark)
- [Blender](benchmarks/blender_benchmark)
- [Matmul](benchmarks/matmul_benchmark)
- [MatmulC++](benchmarks/matmulCpp_benchmark)
- [TensorFlow Real Time Benchmarks](benchmarks/tensorflow_benchmark)
- [MNIST FCNN](benchmarks/MNIST_FCNeuralNetwork)
- [Unigine Heaven](benchmarks/phoronix-unigine-heaven-1.6.5)
- [Unigine Valley](benchmarks/phoronix-unigine-valley-1.1.8)

## [Licenses](LICENSE)
