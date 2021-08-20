## Blender Benchmark

Blender benchmark offers running graphical benchmarks in the background and reporting corresponding stats. More about blender benchmark can be found on it's [website](https://www.blender.org/news/introducing-blender-benchmark/). 


Blender scenes support for different blender versions:

-----------------------------------------------------------------------------------
| Blender Version  | ||                           Scenes                         |||            
|------------------|--------|-----------|-----------|-------|--------------------|
|                  |  bmw27 | classroom | fishy_cat | koro  | pavillon_barcelona |   
| 2.93.1           |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.92            |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.91.2          |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.90.1          |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.90            |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.83            |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
|  2.82            |   ✅   |     ✅    |      ✅   |   ✅  |          ✅        |
-----------------------------------------------------------------------------------

* victor scene is also available, but causes blender to exit

### Devices supported:
✅ CPU 
✅ GPU (Tested:CUDA)

- The Benchmark can run either on GPU os CPU by setting device_type appropriately (tested: CUDA, GPU) in settings.json.

- The benchmark responds to **verbosity** in the range of 0-3 (integer value).

Official Blender Benchmark CLI [docs](./README.txt).
