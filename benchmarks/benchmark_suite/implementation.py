from common.benchmark_wrapper import BenchmarkWrapper
import json
from utils import get_benchmark_module
from celery import Celery
from celery.utils.log import get_task_logger
from celery import Celery
from ..dummy_classifier import implementation


# app = Celery("tasks", backend="rpc://", broker="amqp://localhost")
# celery_log = get_task_logger(__name__)


class BenchmarkSuite:
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.benchmarkArray.append(implementation.DummyClassifier())
        # self.benchmarkArray.append(dummy_regressor.DummyRegressor())
        

    def startBenchmark(self):
        for b in self.benchmarkArray:
            b.startBenchmark()

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):                                           
        with open("config/benchmarkconfig.json") as f:
            self.bench_config = json.load(f)


# @app.task(max_retries=3, soft_time_limit=5)
# def task():
#     BenchmarkSuite().startBenchmark()
#     celery_log.info("Task was completed")
#     return "OK"
