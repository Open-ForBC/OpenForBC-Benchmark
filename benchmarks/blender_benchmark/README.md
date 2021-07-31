## Blender Benchmark

Blender benchmark offers running graphical benchmarks in the background and reporting corresponding stats. More about blender benchmark can be found on it's [website](https://www.blender.org/news/introducing-blender-benchmark/). 

Running help on blender benchmark get-settings command returns the following possible operations.

```
The Blender Open Data Benchmark launcher command line interface

Available Commands:
  authenticate Request a new authentication token
  benchmark    Benchmark scenes
  blender      Commands for managing Blender versions
  clear_cache  Removes all downloaded assets
  devices      List the devices which can be benchmarked
  help         Help about any command
  interactive  Run the launcher in interactive mode (the default command)
  scenes       Commands for managing scenes

Flags:
      --browser           open the verification URL in the browser
  -h, --help              help for benchmark-launcher-cli
  -v, --verbosity uint8   control verbosity (0 = no logs, 1 = error logs (default), 2 = debug logs, 3 = dump blender output) (default 1)
      --version           version for benchmark-launcher-cli
```

All of which can be accessed by using our interfaced script
```python
python3 user_interfaces/cli.py get-settings -b blender-benchmark <command>
```  

Official Blender [docs](bin/README.txt).
