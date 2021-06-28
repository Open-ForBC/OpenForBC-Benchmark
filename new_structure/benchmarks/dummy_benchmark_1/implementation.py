from common.benchmark_wrapper import BenchmarkWrapper

import json

class DummyBenchmark1(BenchmarkWrapper):
    def __init__(self):
        with json.load(open("./benchmark_info.json")) as j:
            self.name = j["name"]
            self.description = j["description"]
            pass

        self.presets = json.load(open("./presets/preset1.json"))

        super()
        pass