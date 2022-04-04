# User guide

## Installation

-   Clone the repository
    ```bash
    git clone --recursive https://github.com/Open-ForBC/OpenForBC-Benchmark.git
    ```

-   Install the `o4bc-bench` tool
    ```bash
    cd OpenForBC-Benchmark
    pip3 install .
    ```

## Usage

Benchmarks can be run interactively by simply launching the `o4bc-bench` command
without any arguments.

The Interactive interface is quite intuitive to navigate around, with
informative prompts to guide you.


For a textual CLI interface, a comprehensive list of arguments can be found
using the following command:

```shell
o4bc-bench --help
```

To get help for a particular command, use:

```shell
o4bc-bench <command:str> --help
```

## Sample commands for the functionality offered by the CLI:

**1. List Benchmarks/Suites:**

```shell
o4bc-bench benchmark list # or `o4bc-bench benchmark` alias
o4bc-bench suite list # or `o4bc-bench suite` alias
```

Get information about a benchmark:

```shell
o4bc-bench benchmark get <benchmark_folder:str>
```

or about a suite:

```shell
o4bc-bench suite get <suite_name:str>

**2. List and get preset information from a particular benchmark:**


```shell
o4bc-bench benchmark list-presets <benchmark_folder:str>
```

for example:

```shell
o4bc-bench benchmark list-presets dummy_benchmark
```

Then obtain information about the preset with:

```shell
o4bc-bench benchmark get-preset <benchmark_folder:str> <preset_name:str>
```

for example:

```shell
o4bc-bench benchmark get-preset dummy_benchmark preset1
```

**3. Run a benchmark/Suite:**


```shell
o4bc-bench benchmark run <benchmark_folder:str> [<preset_name:str>]...
o4bc-bench suite run <suite-name:str>
```
for example:

```shell
o4bc-bench benchmark run dummy_benchmark preset1
```

**4. Build a suite:**
```shell
o4bc-bench suite create
```

## Logs for benchmarks/suites

Logs for each benchmark run can be found in ```/logs``` directory. Each run is
saved by the following format:


```<benchmark_name>/<yyyymmdd_hhmmss>/<phase>_<preset>.<command_number>.<out/err>.log```

Field `<preset>` is not present in setup and cleanup task phases and
`<command_number>` is only preset if there are multiple commands in the phase.
_stdout_ and _stderr_ are kept in separate files.


## View format

Many commands use a pretty table format by default, which can by disabled by
passing the option `--no-table` or `-T`. Some commands, such as `benchmark run`,
`benchmark get-preset`, `benchmark get` and `suite run` support output in json
format, which can be enabled by passing `--json` or `-j`.
