# Developer Documentation

For running a benchmark check [user-guide.md](user-guide.md)
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

- Information about the benchmark is stored in ```benchmark_info.json``` with keys labelled as ```name```, ```description```,```implementation file``` and ```class name``` next to their corresponding values.

- Settings associated to the benchmark are placed in settings folder, to be saved as a json file. You can save more than one settings and select the one you want to run the benchmark with later when running the benchmark. 

