# Gettings Started 

- Guide to developer [docs](developer-guide.md).
- Installation [README](../README.md).

## Usage

Benchmarks can be run interactively using the following command.

```shell
 python3 user_interfaces/cli.py interactive
```

On supported systems (supporting symlinks) one can opt to replace `python3 user_interfaces/cli.py` with `o4bc-bench`.
The following documentation will rely on the symlink.

The Interactive interface is quite intuitive to navigate around, with informative prompts to guide you. 


For a textual CLI interface, a comprehensive list of arguments can be found using the following command:

```shell
./o4bc-bench --help
```

To get help for a particular command, use:

```shell
./o4bc-bench <command:str> --help
```

## Sample commands for the functionality offered by the CLI:

**1. List Benchmarks/Suites:**  

```shell
./o4bc-bench list-benchmarks
./o4bc-bench list-suites
```

**2. Get settings from a particular benchmark:**


```shell
./o4bc-bench get-settings -b <benchmark-name:str> -s <benchmark-settings:str>
```
for example:

```shell
./o4bc-bench get-settings -b dummy_benchmark -s settings1.json
```
or if you'd like to list all settings for a benchmark, you can check them using the following command

```shell
./o4bc-bench get-settings -b dummy_benchmark 
```


**3. Run a benchmark/Suite:**


```shell 
./o4bc-bench run-benchmark -b <benchmark-name:str> -s <settings:str> -v <verbosity:int> 
./o4bc-bench run-suite <suite-name:str> 
```
for example:

```shell
./o4bc-bench run-benchmark -b dummy_benchmark -s settings1.json -v 1 
```

**4. Build a suite:**
```shell
./o4bc-bench make-suite --name <suite-name:str> -b <benchmark-name:str> -s <settings:str> -f <file-name:str> -d <description(optional):str>
```
for example:

```shell
./o4bc-bench make-suite --name Mysuite -b dummy_benchmark -s settings1.json -f my_suite -d "This is demo description."  
```


## Logs for benchmarks/suites

Logs for each run can be found in ```/logs``` directory. Each run is saved by the following format:

- For stand-alone benchmarks:

```<benchmark_name>/<settings>/<yyyymmdd_hhmmss>/output.log``` 
- For suites:

```<suite_name>/<yyyymmdd_hhmmss>/output.log ```

Logs can be listed with the following command

```shell
./o4bc-bench list-logs
```

## View format

Commands like ```list-logs``` , ```list-benchmarks``` , ```list-suites``` and  ```get-settings``` support viewing in pretty table format by default. To view as a csv use --csv flags with the command.
