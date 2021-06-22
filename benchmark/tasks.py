from re import L
from celery import Celery
from interface_skeleton import InterfaceSkeleton

app = Celery('tasks', backend='rpc://', broker='amqp://localhost')
app.conf.task_serializer = 'json'

"""
TASKS:
(Main)1.Run the benchmark
2.Get the config (The running of the benchmark would be depenedent on this)
3. Check for process completion
4. Listen for key presses while the process runs
5. Add the logs in the logger file
"""


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



# def my_monitor(app):
#     state = app.events.State()

#     def announce_failed_tasks(event):
#         state.event(event)
#         # task name is sent only with -received event, and state
#         # will keep track of this for us.
#         task = state.tasks.get(event['uuid'])

#         print('TASK FAILED: %s[%s] %s' % (
#             task.name, task.uuid, task.info(),))

#     with app.connection() as connection:
#         recv = app.events.Receiver(connection, handlers={
#                 'task-failed': announce_failed_tasks,
#         })
#         recv.capture(limit=None, timeout=None, wakeup=True)

# if __name__ == '__main__':
#     app = Celery(broker='amqp://guest@localhost//')
#     my_monitor(app)













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


