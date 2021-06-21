from re import L
from celery import Celery
from interface_skeleton import InterfaceSkeleton

app = Celery('tasks', backend='rpc://', broker='amqp://localhost')
app.conf.task_serializer = 'json'

# class BaseTask(app.Task):
#     """Abstract base class for all tasks in my app."""

#     abstract = True

#     def on_retry(self, exc, task_id, args, kwargs, einfo):
#         """Log the exceptions to sentry at retry."""
#         sentrycli.captureException(exc)
#         super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         """Log the exceptions to sentry."""
#         sentrycli.captureException(exc)
#         super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

@app.add_periodic_task
def autoTerminate():
    pass


@app.task
# (bind=True,
    # max_retries=3,
    # soft_time_limit=5,
    # base=BaseTask)
def run():
    ins = InterfaceSkeleton()
    ins.loadConfig()
    out = ins.startBenchmark()
    print(out)
