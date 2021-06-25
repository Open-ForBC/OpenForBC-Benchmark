from celery.utils.log import get_task_logger
import sys
sys.path.append('../')
# from benchmark.benchmark_suite import BenchmarkSuite
from dummy_classifier import DummyClassifier
from celery import Celery

app = Celery('tasks', backend='rpc://', broker='amqp://localhost')

celery_log = get_task_logger(__name__)


class BaseTask(app.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@app.task(max_retries=3,
    soft_time_limit=5,
    base=BaseTask)
def startBenchmark():
    DummyClassifier(None).startBenchmark()
    celery_log.info("Task was completed")
    return 'OK'
