# Developer Documentation

- To run benchmarks check the [user-guide.md](user-guide.md).
- Installation [README](../README.md).

## Tool development environment

The packaging tool used by the _OpenForBC-Benchmark_ tool is
[poetry](https://python-poetry.org). _Poetry_ allows for a easy development
experience thanks to python's virtual environments.

Poetry creates virtual environments a cache folder by default, if you prefer to
keep the virtualenv inside the project's directory you can configure poetry to
do so (`poetry config virtualenvs.in-project true`).

> NOTE: When using out of project virtualenvs the prompt can become a little bit
> too long because of the virtualenv folder name, but this can be fixed by
> adding the `prompt = "venv"` line to the `pyvenv.cfg` file present in the
> virtualenv folder (which can be obtained by running `poetry env list
> --full-path`).

To install all the dependencies in the virtualenv (eventually creating it if it
doesn't exist already) run `poetry install`.

After the dependencies are installed you can run commands inside the virtualenv
by using `poetry run <command>` (e.g. `poetry run pytest`, `poetry run
o4bc-bench`) or activate the virtual environment with `poetry shell`, which will
get you into a shell where you can directly run commands inside the virtualenv.

### Pre-commit for local commit checks

If you want to run linter and type checks locally before every commit you can
install [pre-commit](https://pre-commit.com/#install): this repo alreaady
contains a `pre-commit-config.yaml` configuration.

You can install and activate _pre-commit_ by running the following commands
(outside of the project's virtual environment):

```shell
pip install pre-commit
pre-commit
```

## Before opening a PR

Continuous integration is setup [here](../.github/workflows/CI.yml). It
currently runs the library and CLI tests.

Before opening a PR, please lint and type check your files by running `poetry
run flake8` and `poetry run mypy`, then check that your changes do not break
anything by executing `poetry run pytest`.

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
can be a [`command`](#commands) which will output benchmark data to *stdout*
when run, or a `match` type object.

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
| `env`          | `object`                |          |
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

The `env` field is an optional object, with values of type `string`, which
specifies additional environment variables which will me merged with the
`run_command` environment.

### Benchmark documentation

As a bare minimum, add a README.md file that documents what the benchmark does
and the settings. For more comprehensive documentation, you can create an
additional doc/ folder and place there additional files.

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

Essentially, there are two modules at work: the `openforbc_benchmark` library
module and the cli interface module (`openforbc_benchmark.cli`).

The library can deserialize JSON definitions and provide the tasks to be
executed in each phase (_setup_, _run_ and _cleanup_), while the CLI provides
the end user with an interface with the library that can run these commands and
extract statistical data from the benchmark's output.

The command line app has two interfaces, a basic command interface or an
interactive UI.
