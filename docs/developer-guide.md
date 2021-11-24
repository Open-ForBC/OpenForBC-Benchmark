# Developer Documentation

- To run benchmarks check the [user-guide.md](user-guide.md).
- Installation [README](../README.md).

## Before opening a PR

Continuous integration is setup [here](../.github/workflows/CI.yml). It
currently runs the CLI test and blender with one setting file.

Before opening a PR, please check that your changes do not break anything by
executing ./test_PR.sh.  This executes full tests: CLI, blender with various
settings, suites.

## Adding a benchmark

Following is the file hierarchy for the benchmarks folder.

```
.
+-- benchmarks
    |-- Sample Benchmark A
    |   |-- benchmark.json                        *
    |   |-- presets                               *
    |   |   +-- preset<#>.json
    |   +-- <benchmark executables/scripts/docs>
    |
    +-- Sample Benchmark B
        |-- benchmark.json                        *
        |-- presets                               *
        |   |-- preset_1.json
        |   +-- preset_1.json
        |-- example_bench
        |-- setup.sh
        +-- cleanup.sh

* Essential for executing benchmark
```

To add a benchmark, create a directory in the benchmarks folder similar to the
sample benchmarks shown above. An example can be found in the dummy benchmark
[implementation](../benchmarks/dummy_benchmark/).

### Benchmark definition

The benchmark definition is a file named `benchmark.json`, which is validated
against the [benchmark definition schema](../jsonschema/benchmark.schema.json)
stored in the *jsonschema* folder in this repository.

#### Benchmark definition schema

Here's an example of a benchmark definition:

```json
{
  "name": "Sample Benchmark A",
  "description": "A sample benchmark",
  "setup_command": "setup.sh --prepare",
  "run_command": {
    "command": "example_bench --gpu",
    "env": {
      "CPU": "0"
    }
  },
  "cleanup_command": "setup.sh --clean",
  "stats": {
    "mult_time_ms": {
      "regex": "Matrix multiplication time: (\\d+)ms"
    }
  },
  "virtualenv": true
}
```

| Field             | Type                 | Required |
| ----------------- | -------------------- | -------- |
| `name`            | `string`             | x        |
| `description`     | `string`             | x        |
| `default_preset`  | `string`             | x        |
| `setup_command`   | *commands*           |          |
| `run_command`     | *commands*           | x        |
| `cleanup_command` | *commands*           |          |
| `stats`           | *command*`\|`*match* | x        |
| `virtualenv`      | `boolean`            |          |

All the metadata fields are __required__: you need to specify the benchmark's
*name* and *description*.

The `default_preset` field (**required**) is the name of the default preset: the
referenced preset **must** be present in the `presets` folder.

##### Commands

There are three main commands used to interface with the benchmark: the
`setup_command` is run before any other command and should be used, for
instance, to install benchmark dependencies or build its binary, the
`run_command` (__required__) is the actual benchmark command, and
`cleanup_command` is used after the benchmark is no longer needed to cleanup.

Every *command* field can be a single instance or an array of `command` type.
The `command` type can be a *string* (the path of the executable to be run) or
an object with the following fields:

| Field     | Type                    | Required |
| --------- | ----------------------- | -------- |
| `command` | `string\|Array<string>` | x        |
| `env`     | `object`                |          |
| `workdir` | `string`                |          |

The `command` field specifies the command to be executed and is __required__.
You can specify both a string, which will be split according to UNIX standard,
or an array of strings consisting of the executable and its arguments. Other
fields in the `command` type may be used to configure the process environment (a
JSON *object* with values of type *string*) and its workdir.

##### Benchmark output

The `stats` field is used to specify how to obtain resulting benchmark data, it
can be a [`command`](#commands) which will output benchmark data to *stdout* when run, or a `match` type object.

Benchmark data written to *stdout* must be a JSON object (its
[schema](../jsonschema/benchmark_stats.schema.json) is stored in the
*jsonschema* folder in this repository) with the name of the
data as key and its value as the actual value.

The `match` type is an object, its keys are the benchmark's output data field
names, while the values are an object specifying how to match the data: it has
two fields: `regex` (a __required__ *string* which contains a regex that is
executed against a file, which __must__ contain a group which will match the
value of this data field) and `file` (an optional *string* which is the file on
whose content the regex will be executed). If no `file` is specified the one
containing output from the *run* command is used.

##### Python virtualenv

The `virtualenv` field specifies whether to create a virtualenv for this
benchmark, which will always be activated before running every command.

### Benchmark presets

Presets associated with the benchmark are placed in the *presets* folder, and
represented by a JSON file (its
[schema](../josnschema/benchmark_preset.schema.json) is stored in the
*jsonschema* folder in this repository).

You can define more than one preset and select the ones you want to run the
benchmark with later when running the benchmark. 

The default preset is specified in the benchmark's definition (field
`default_preset`)  and must be defined.

#### Benchmark preset schema

Here's an example of a valid benchmark preset JSON file:

```json
{
  "args": "--config=preset_57.conf",
  "init_command": "setup_preset.sh preset_57.conf",
  "post_command": "setup_preset.sh --teardown"
}
```

The object schema is:

| Field          | Type                    | Required |
| -------------- | ----------------------- | -------- |
| `args`         | `string\|Array<string>` | x        |
| `init_command` | *commands*              | x        |
| `post_command` | *commands*              |          |

Only one of `args` and `init_command` is required, you do not need (but can if
needed) to specify both.

The *command* fields use the same schema that the [main benchmark definition
commands](#commands) use.

`args` is a `string` containing arguments to be passed to the benchmark's *run*
command. You can also specify an array of strings as the `args` field if you
need to use spaces inside arguments or you want to be directly specify *argv*
components.

### Benchmark documentation

As a bare minimum, add a README.md file that documents what the benchmark does
and the settings. For more comprehensive documentation, you can create an
additional doc/ folder and place there additional files.

### Benchmark tests

Please consider adding tests for your benchmark in bin/, and also if appropriate
add them to CI or test_PR.sh


## Adding a benchmark suite

Following is the hierarchy of the suites folder.

```
.
+-- suites
    |-- suite1.json
    +-- suite2.json
```

### Benchmark suite

The suite definition is a JSON file validated against the [benchmark suite
definition
schema](../openforbc_benchmark/jsonschema/benchmark_suite.schema.json) which is
stored in the `openforbc_benchmark/jsonschema` folder in this repository.

#### Benchmark suite definition schema

Here's an example of a benchmark suite definition:

```json
{
  "name": "Sample suite",
  "description": "A sample benchmark suite",
  "benchmark_runs": [ {
    "benchmark_folder": "dummy_bench",
    "presets": [ "preset1", "preset2" ]
  } ]
}
```

| Field            | Type                   | Required |
| ---------------- | ---------------------- | -------- |
| `name`           | `string`               | x        |
| `description`    | `string`               | x        |
| `benchmark_runs` | `Array<benchmark_run>` | x        |

All the fields are __required__.

##### Benchmark runs

The `benchmark_runs` field is an array of `benchmark_run` objects.

Each `benchmark_run` is an object with two __required__ fields:

- `benchmark_folder`: the folder containing the benchmark
- `presets`: a single or an array of preset names (`string`)

## How the tool works

Essentially, there are two modules at work, ie. Benchmark Suite and Benchmark
Factory which extends the interface defined in Benchmark Wrapper.

The Benchmark Factory is a factory method that takes in the benchmark name and
optionally a settings file and returns the benchmark object.

The Benchmark Suite looks for a JSON configuration of benchmark to run as a
combo in ```benchmark_info.json``` and runs all the benchmarks in a loop.

To communicate the above to end-user, there are three outlets: GUI, CLI and
daemon defined in the ```user_interfaces``` directory. Channeled by the
interface skeleton which also uses the benchmark wrapper interface.

Further, the benchmark implementations also adhere to the Benchmark Wrapper
interface.

The class diagram for the project can be found
[here](../assets/class_diagram.svg).
