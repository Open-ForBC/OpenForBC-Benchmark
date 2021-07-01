import json
import os

# from celery.utils.log import get_task_logger
# from celery import Celery
from ..common.benchmark_factory import BenchmarkFactory
import pathlib

# app = Celery("tasks", backend="rpc://", broker="amqp://localhost")
# celery_log = get_task_logger(__name__)


class BenchmarkSuite:
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()


    def startBenchmark(self):
        self.getBenchmarkConfig()
        for key in self.bench_config.keys():
            self.benchmarkArray.append(
                BenchmarkFactory().getBenchmarkModule(
                    file_path=os.path.join("benchmarks", key)
                )
            )
        for benchmark in self.benchmarkArray:
            run = benchmark.getCallable()
            run()

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        with open(pathlib.Path.cwd().joinpath('benchmarks','benchmark_suite','suite_info.json')) as config:
            self.bench_config = json.load(config)


# if __name__ == "main":
#     BenchmarkSuite().startBenchmark()

# @app.task(max_retries=3, soft_time_limit=5)
# def task():
#     BenchmarkSuite().startBenchmark()
#     celery_log.info("Task was completed")
#     return "OK"
