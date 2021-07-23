# Developer Documentation

For running a benchmark check [user-guide.md](user-guide.md).
## Adding a benchmark 

Following is the file hierarchy for the benchmarks folder.
```
.
├── benchmarks
│   ├── Sample Benchmark A
│   │   ├── benchmark_info.json                     *
│   │   ├── bin <contains executables/docs etc>
│   │   ├── implementation.py                       *
│   │   ├── settings                                *
│   │   │   ├── settings1.json
│   │   └── setup.py
│   └── Sample Benchmark B
│       ├── benchmark_info.json                     *
│       ├── implementation.py                       *
│       └── settings                                *
│       |   ├── settings1.json
│       |   └── settings2.json
        └── setup.sh
* Essential for executing benchmark
```
To add a benchmark, create a directory in the benchmarks folder similar to the Sample Benchmark directory as shown above.

-  The Benchmark implementation goes into the ```implementation.py``` folder. 

- Information about the benchmark is stored in ```benchmark_info.json``` with keys labeled as ```name```, ```description```,```implementation file``` and ```class name``` next to their corresponding values.

- Settings associated with the benchmark are placed in the settings folder, to be saved as a JSON file. You can save more than one setting and select the one you want to run the benchmark with later when running the benchmark. 

## How the tool works

Essentially, there are two modules at work, ie. Benchmark Suite and Benchmark Factory which extends the interface defined in Benchmark Wrapper.

The Benchmark Factory is a factory method that takes in the benchmark name and optionally a settings file and returns the benchmark object.

The Benchmark Suite looks for a JSON configuration of benchmark to run as a combo in ```benchmark_info.json``` and runs all the benchmarks in a loop.

To communicate the above to end-user, there are three outlets: GUI, CLI and daemon defined in the ```user_interfaces``` directory. Channeled by the interface skeleton which also uses the benchmark wrapper interface.

Further, the benchmark implementations also adhere to the Benchmark Wrapper interface.

The class diagram for the project can be found [here](assets/class_diagram.svg).
