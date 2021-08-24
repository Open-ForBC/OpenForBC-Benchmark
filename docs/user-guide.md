# Gettings Started 

- Guide to developer [docs](developer-guide.md).
- Installation [README](../README.md).

## Usage

Benchmarks can be run interactively using the following command.

```shell
 python3 user_interfaces/cli.py interactive
```

The Interactive interface is quite intuitive to navigate around, with informative prompts to guide you. 


For a textual CLI interface, a comprehensive list of arguments can be found using the following command:

```shell
python3 user_interfaces/cli.py --help
```

To get help for a particular command, use:

```shell
python3 user_interfaces/cli.py <command:str> --help
```

## Sample commands for the functionality offered by the CLI:

**1. List Benchmarks/Suites:**  

```shell
python3 user_interfaces/cli.py list-benchmarks
python3 user_interfaces/cli.py list-suites
```

**2. Get settings from a particular benchmark:**


```shell
python3 user_interfaces/cli.py get-settings -b <benchmark-name:str> -s <benchmark-settings:str>
```
for example:

```shell
python3 user_interfaces/cli.py get-settings -b dummy_benchmark -s settings1.json
```
or if you'd like to list all settings for a benchmark, you can check them using the following command

```shell
python3 user_interfaces/cli.py get-settings -b dummy_benchmark 
```


**3. Run a benchmark/Suite:**


```shell 
python3 user_interfaces/cli.py run-benchmark -b <benchmark-name:str> -s <settings:str> -v <verbosity:int> 
python3 user_interfaces/cli.py run-suite <suite-name:str> 
```
for example:

```shell
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1 
```

**4. Build a suite:**
```shell
python3 user_interfaces/cli.py make-suite --name <suite-name:str> -b <benchmark-name:str> -s <settings:str> -f <file-name:str> -d <description(optional):str>
```
for example:

```shell
python3 user_interfaces/cli.py make-suite --name Mysuite -b dummy_benchmark -s settings1.json -f my_suite -d "This is demo description."  
```


## Logs for benchmarks/suites

Logs for each run can be found in ```/logs``` directory. Each run is saved by the following format:

- For stand-alone benchmarks:

```<benchmark_name>/<settings>/<yyyymmdd_hhmmss>/output.log``` 
- For suites:

```<suite_name>/<yyyymmdd_hhmmss>/output.log ```

Logs can be listed with the following command

```shell
python3 user_interfaces/cli.py list-logs
```

## View format

Commands like ```list-logs``` , ```list-benchmarks``` , ```list-suites``` and  ```get-settings``` support viewing in pretty table format by default. To view as a csv use --csv flags with the command.
