# Gettings Started 

## Usage

Benchmarks can be run interactively using the following command.

```python
 python3 user_interfaces/cli.py interactive
```

Interactive interface is quite intuitive to navigate around, with informative prompts to guide you. 


For a textual CLI interface, you can use the following commands

**1. List Benchmarks/Suites:**  

``` 
python3 user_interfaces/cli.py list-benchmarks -v <int>
python3 user_interfaces/cli.py list-suites
```

**2. Get settings from a particular benchmark:**


```python
python3 user_interfaces/cli.py get-settings <benchmark> <benchmark-settings>
```
for example

```
python3 user_interfaces/cli.py get-settings blender_benchmark scenes list
```

**3. Run a benchmark/Suite:**


```python 
python3 user_interfaces/cli.py run-benchmark <name of benchmark> 
python3 user_interfaces/cli.py run-suite <name of suite> 
```
for example

```python
python3 user_interfaces/cli.py run-benchmark dummy_benchmark
```


All the above commands can be referred by using the following command 
```python
python3 user_interfaces/cli.py --help
```

