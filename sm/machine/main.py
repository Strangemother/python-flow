"""Run as a queue requesting service for all heavy request tasks.
"""
import os
import time

from gevent import monkey; monkey.patch_all()
from huey import SqliteHuey


from machine import django_connect
django_connect.safe_bind()

from machine import engine, models

# The remote running lib.
huey = SqliteHuey(filename='sm-huey.db')

@huey.task()
def run_flow(flow_id, task=None, *a, **kw):
    """Running within the machine context, accept the flow id, gather a django
    Flow model and run `engine.run_all_flow(flow)`.
    """
    tid = task if task else "NO-TASK"
    print('Run a huey flow', flow_id, tid)
    flow = models.Flow.objects.get(pk=flow_id)
    # The next action is given back though the rpc context and captured by
    #  signals. All content should be picklable.
    # The next action may be a huey task or a simple value marking
    #  the end of the flow.
    flow_result = engine.run_all_flow(flow, *a, **kw)
    return flow_result


@huey.task()
def run_sub_task_script(script, *a, parent_id=None, **kw):
    print('Run sub task script', script, parent_id, a, kw)
    return engine.run_script(script, *a, **kw)


def submit_flow(flow_or_id, *a, **kw):
    """Called from django view or another importing  app, _submit_ the flow
    as a task and routine to run within the machine engine.
    Call to the method existing on the connected rpc `run_flow` with the given
    id. Return the Task id of the huey Task.

    The new task id is stored in the flow.owner, the run_flow function calls
    to engine.run_all_flow, performing all required changes to the db.
    If a django Flow model is given, the pk is used.

        submit_flow(1)
        submit_flow(flow)
    """
    flow = flow_or_id
    if isinstance(flow_or_id, int):
        flow = models.Flow.objects.get(pk=flow_or_id)

    res = run_flow(flow.pk, *a, **kw)
    task_id = res.id
    flow.owner = task_id
    flow.save()
    print('Task submitted', task_id)
    return task_id


@huey.on_startup()
def open_db_connection():
    django_connect.safe_bind()


@huey.post_execute()
def post_execute_hook(task, task_value, exc):
    # Post-execute hooks are passed the task, the return value (if the task
    # succeeded), and the exception (if one occurred).
    print('!! Task complete', task, "\n", task_value)
    if exc is not None:
        print('Task "%s" failed with error: %s!' % (task.id, exc))
    # v = vv.report(10)
    if isinstance(task_value, engine.Signal):
        if task_value.stop_flow is True:
            print('!! Will not continue because stop_flow is True\n', task_value)
        else:
            oid = task_value.owner
            print('Relooping flow.', oid)

        if hasattr(task_value, 'spawn'):
            spawn_task(task, task_value)
            # Add the subtask id to the parent
        else:
            print('x  Signal has no spawn "signal.spawn"', task_value)

def spawn_task(task, task_value):
    args = getattr(task_value, 'args', ())
    kwargs = getattr(task_value, 'kwargs', {})
    print('^  spawn', task_value.spawn, args, kwargs)

    if 'parent_id' in kwargs:
        print('   spawn had an extra "parent_id" argument', kwargs)
        del kwargs['parent_id']

    res = run_sub_task_script(task_value.spawn,
        *args, **kwargs, parent_id=task.id)
    print('^  Spawn ID', res.id)
    con = models.TaskConnection(
        owner=task.id,
        task_id=res.id
    )
    con.save()

    return res
