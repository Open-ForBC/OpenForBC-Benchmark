from benchmark.benchmark_wrapper import BenchmarkWrapper
import json
from utils import get_benchmark_module
from celery import Celery
from celery.utils.log import get_task_logger
from celery import Celery


app = Celery("tasks", backend="rpc://", broker="amqp://localhost")
celery_log = get_task_logger(__name__)


class BenchmarkSuite:
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray: BenchmarkWrapper = []
        self.bench_config = {}

    def startBenchmark(self, benchmark):
        try:
            bm_module, _ = get_benchmark_module(benchmark)
        except ImportError as e:
            raise e
        run = bm_module.get_callable("classifier")
        res = run()

        return res

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        with open("config/benchmarkconfig.json") as f:
            self.bench_config = json.load(f)


@app.task(max_retries=3, soft_time_limit=5)
def task():
    print(BenchmarkSuite().startBenchmark("benchmark/dummy_benchmark"))
    celery_log.info("Task was completed")
    return "OK"
