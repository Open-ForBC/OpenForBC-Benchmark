# Developer Documentation

- To run benchmarks check the [user-guide.md](user-guide.md).
- Installation [README](../README.md).

## Before opening a PR

Continuous integration is setup [here](../.github/workflows/CI.yml). It currently runs the CLI test and blender with one setting file.

Before opening a PR, please check that your changes do not break anything by executing ./test_PR.sh.
This executes full tests: CLI, blender with various settings, suites.

## Adding a benchmark 

Following is the file hierarchy for the benchmarks folder.
```
.
├── benchmarks
│   ├── Sample Benchmark A
│   │   ├── README.md                               
│   │   ├── benchmark_info.json                     *
│   │   ├── bin <contains executables/docs etc>
│   │   ├── implementation.py                       *
│   │   ├── settings                                *
│   │   │   ├── settings1.json
│   │   └── setup.py
│   └── Sample Benchmark B
|   |   ├── README.md                               
│       ├── benchmark_info.json                     *
│       ├── implementation.py                       *
│       └── settings                                *
│       |   ├── settings1.json
│       |   └── settings2.json
        └── setup.sh

* Essential for executing benchmark
```
To add a benchmark, create a directory in the benchmarks folder similar to the Sample Benchmark directory as shown above. An example can be found in the dummy benchmark [implementation](../benchmarks/dummy_benchmark/). 

-  The Benchmark implementation goes into ```implementation.py```. 

- Information about the benchmark is stored in ```benchmark_info.json``` with keys labeled as ```name```, ```description```,```implementation file``` and ```class name``` next to their corresponding values. Declaring file and class name allows for an easier file search while maintaining uniformity. You can choose to give it any name as long as it ends with a python extension(.py).

- Settings associated with the benchmark are placed in the settings folder, to be saved as a JSON file. You can save more than one setting and select the one you want to run the benchmark with later when running the benchmark. 

- To properly propagate the execution logs, return the logs as a dictionary with the format ```{"output":<logging data>}``` from the method responsible for running the benchmark, ie. ```startBenchmark()``` in usual cases.

- *Documentation.* As a bare minimum, add a README.md file that documents what the benchmark does and the settings. For more comprehensive documentation, you can create an additional doc/ folder and place there additional files.

- *Continuous integration* (CI). Please consider adding tests for your benchmark in bin/, and also if appropriate add them to CI or test_PR.sh 

## How the tool works

Essentially, there are two modules at work, ie. Benchmark Suite and Benchmark Factory which extends the interface defined in Benchmark Wrapper.

The Benchmark Factory is a factory method that takes in the benchmark name and optionally a settings file and returns the benchmark object.

The Benchmark Suite looks for a JSON configuration of benchmark to run as a combo in ```benchmark_info.json``` and runs all the benchmarks in a loop.

To communicate the above to end-user, there are three outlets: GUI, CLI and daemon defined in the ```user_interfaces``` directory. Channeled by the interface skeleton which also uses the benchmark wrapper interface.

Further, the benchmark implementations also adhere to the Benchmark Wrapper interface.

The class diagram for the project can be found [here](../assets/class_diagram.svg).
