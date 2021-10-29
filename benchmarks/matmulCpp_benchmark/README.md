# Matrix Multiplication Benchmark: C++ version

## Introduction:

This simple benchmark perform multiplication between two matrices reporting the time of execution of the computation.

## Settings:

Through the settings json file it's possible to choose the size of the two matrices. Each setting file contain a couple of values that correspond two the number of row and column of the matrices. So, if the setting file contains the two values "dimension1" and "dimension2", the first matrix will be "dimension1"x"dimension2", while the second will be "dimension2"x"dimension1". The two dimensions are reported in the setting file name.

## Devices supported:

The computation is performed on the CPU

## How to test the benchmark (Linux)

To run the benchmark test type the command ./bin/test_matmulCpp.sh on a terminal . The test runs the benchmark with default setting defined in benchmark_info and it shows the logs list.
