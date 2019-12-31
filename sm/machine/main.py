"""Run as a queue requesting service for all heavy request tasks.
"""
import os
import time

from gevent import monkey; monkey.patch_all()
from huey import SqliteHuey


from machine import django_connect
django_connect.safe_bind()

from machine import engine, models

from machine.log import p_cyan_log
log = p_cyan_log('main')


# The remote running lib.
huey = SqliteHuey(filename='sm-huey.db')


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

    # offload to online
    res = run_flow(flow.pk, *a, **kw)
    task_id = res.id
    flow.owner = task_id
    flow.save()
    return task_id


@huey.task()
def run_flow(flow_id, *a, **kw):
    """Running within the machine context, accept the flow id, gather a django
    Flow model and run `engine.run_all_flow(flow)`.
    """
    log('Run a huey flow', flow_id, a, kw)
    flow = models.Flow.objects.get(pk=flow_id)
    # The next action is given back though the rpc context and captured by
    #  signals. All content should be picklable.
    # The next action may be a huey task or a simple value marking
    #  the end of the flow.
    flow_result = engine.run_all_flow(flow, *a, **kw)
    return flow_result


@huey.task()
def run_sub_task_script(script, *a, parent_id=None,
    parent_args=None, parent_kwargs=None, **kw):
    log('Run sub task script', script, parent_id, a, kw)
    res = engine.run_script(script, *a, **kw)
    #res = engine.run_script(script, *a, **kw)
    return engine.spawn_result(
        result=res,
        parent_id=parent_id,
        _args=parent_args,
        _kwargs=parent_kwargs,
        )


@huey.on_startup()
def open_db_connection():
    django_connect.safe_bind()


@huey.post_execute()
def post_execute_hook(task, task_value, exc):
    # Post-execute hooks are passed the task, the return value (if the task
    # succeeded), and the exception (if one occurred).
    log('!! Task complete', task, "\n", task_value)
    if exc is not None:
        log('Task "%s" failed with error: %s!' % (task.id, exc))
    # v = vv.report(10)
    if isinstance(task_value, engine.Signal):
        signal_response(task, task_value)


def signal_response(task, sig_result):
    if sig_result.stop_flow is True:
        log('!! Will not continue because stop_flow is True\n', sig_result)
    else:
        oid = sig_result.owner
        log('Relooping flow.', oid)

    if hasattr(sig_result, 'spawn'):
        spawn_task(task, sig_result)
        # Add the subtask id to the parent

    else:
        log('x  Signal has no spawn "signal.spawn"', sig_result)

    if sig_result.name == 'spawn_result':
        log('spawn result:', sig_result.name)
        store_subtask_and_contine(task, sig_result)
        # an answer to a spawn to resolve to a flow
        # and restart the flow if required.


def store_subtask_and_contine(task, sig_result):
    pid = sig_result.parent_id
    log('Task value parent: ', pid)
    flow = models.Flow.objects.get(owner=pid)
    #make_connection(pid, task.id)

    log('resubmitting', flow.id, dir(sig_result))
    current_task = engine.get_current_task(flow)
    result = sig_result.result
    engine._save_flow_and_step(flow, result, current_task)
    parent_args = sig_result._args
    parent_kwargs = sig_result._kwargs
    submit_flow(flow.id, *parent_args, **parent_kwargs)

    # save the result in the given flow.
    # Continue flow if required.

    # The task sig_result has a parent; the original owner of the
    # task. Resolve the flow and return the current task,
    # Add the result as a task_step and continue.
    #
    # The task should have a spawn object to resolve to, storing
    # its task_result against the key and task id of the
    # given content.


def make_connection(owner_id, task_id):
    con = models.TaskConnection(
        owner=owner_id,
        task_id=task_id
    )
    con.save()
    return con


def spawn_task(task, sig_result):
    args = getattr(sig_result, 'args', ())
    kwargs = getattr(sig_result, 'kwargs', {})
    log('^  spawn', sig_result.spawn, args, kwargs)

    _args = getattr(sig_result, '_args', ())
    _kwargs = getattr(sig_result, '_kwargs', {})

    if 'parent_id' in kwargs:
        log('   spawn had an extra "parent_id" argument', kwargs)
        del kwargs['parent_id']

    task_job = run_sub_task_script(
        sig_result.spawn,
        *args, **kwargs,
        parent_id=task.id,
        parent_args=_args,
        parent_kwargs=_kwargs,
        )

    log('^  Spawn ID', task_job.id)

    # add the new Task connection to the owner task(flow by task id.)
    # without a complete flag.
    add_spawn_to_flow(task, task_job)
    return task_job


def add_spawn_to_flow(task, task_job):
    # store the new spawn task to the owner flow as an ID connection
    # When the task is done - calling _post_, the parent_id is
    # this owner id, to continue a WAIT flow.
    conn = make_connection(task.id, task_job.id)
    try:
        flow_model = models.Flow.objects.get(owner=task.id)
        flow_model.spawn.add(conn)
        log('*  Good. Spawn saved against flow.')
    except models.Flow.DoesNotExist:
        log('x  Attemping to access flow failed due to DNI:', task.id)
