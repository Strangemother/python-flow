"""Run as a queue requesting service for all heavy request tasks.
"""
import os
import time

from gevent import monkey; monkey.patch_all()
from huey import SqliteHuey


from machine import django_connect
django_connect.safe_bind()

from machine import engine, models, create
from machine.flow import run_all_flow, store_flow_and_step, fail_flow, store_and_step
from machine.script import run_script
from machine.signal import Signal, spawn_result
from machine.task import get_current_task, get_routine_task
from machine.log import p_cyan_log
log = p_cyan_log('main')


# The remote running lib.
huey = SqliteHuey(filename='sm-huey.db')


def submit_create_flow(routine, *a, routine_name=None, init_flow_position=0, **kw):
    """Start the processing of a new flow given the _routine_ to process.
    Return a tuple of the newly created flow and flow task ID.
    """
    flow = create.create_flow(routine, init_flow_position, routine_name)
    fid = submit_flow(flow, *a, **kw)
    return (flow, fid,)


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
    # flow = flow_or_id
    # if isinstance(flow_or_id, int):
    #     flow = models.Flow.objects.get(pk=flow_or_id)
    flow = get_flow(flow_or_id)
    # offload to online
    print('== Submit flow', kw)
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
    flow = get_flow(flow_id)
    log('+ Task', flow.routine.name, a, kw)
    #flow = models.Flow.objects.get(pk=flow_id)
    # The next action is given back though the rpc context and captured by
    #  signals. All content should be picklable.
    # The next action may be a huey task or a simple value marking
    #  the end of the flow.
    flow_result = run_all_flow(flow, *a, **kw)
    return flow_result


@huey.task()
def run_sub_task_script(script, *a, parent_id=None,
    parent_args=None, parent_kwargs=None, **kw):
    log('Run sub task script', script, parent_id, a, kw)
    res = run_script(script, *a, **kw)
    #res = engine.run_script(script, *a, **kw)
    #return engine.spawn_result(
    return spawn_result(
        result=res,
        parent_id=parent_id,
        _args=parent_args,
        _kwargs=parent_kwargs,
        all_flow_results=kw.get('all_flow_results', None)
        )


@huey.on_startup()
def open_db_connection():
    django_connect.safe_bind()


@huey.post_execute()
def post_execute_hook(task, task_value, exc):
    # Post-execute hooks are passed the task, the return value (if the task
    # succeeded), and the exception (if one occurred).
    log('!! Task complete', task, "\n", task_value)
    # v = vv.report(10)
    #

    if isinstance(task_value, Signal):
        signal_response(task, task_value)

    if exc is not None:
        log('ERROR', exc)
        flow = models.Flow.objects.get(owner=task.id)
        fail_flow(flow, exc, task)
        # engine.flow.fail_flow(flow, exc, task)
        return False


def get_flow(flow_or_id):
    flow = flow_or_id
    if isinstance(flow_or_id, int):
        flow = models.Flow.objects.get(pk=flow_or_id)
    return flow


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

    log('resubmitting', flow.id, flow.state, sig_result)
    try:
        current_task = get_current_task(flow)
        # current_task = engine.get_current_task(flow)
    except IndexError as e:
        log(f'!! Cannot resubmit "{sig_result.name}" due to IndexError {e}')
        current_task = None
        if sig_result.name == 'spawn_result':
            # The last action was a long-process.
            # Therefore yield the last Task in the flow
            log('... However, spawn_result - Testing the last flow task')
            current_task = get_routine_task(flow.routine, -1)
            # current_task = engine.get_routine_task(flow.routine, -1)

    result = sig_result.result
    #engine.store_flow_and_step(flow, current_task, result, )
    store_and_step(flow, current_task, result, )
    parent_args = sig_result._args
    parent_kwargs = sig_result._kwargs
    all_flow_results = sig_result.all_flow_results
    parent_kwargs.setdefault('all_flow_results', all_flow_results)

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


def spawn_task(orig_task, sig_result):
    args = getattr(sig_result, 'args', ())
    kwargs = getattr(sig_result, 'kwargs', {})
    log('^  spawn', sig_result.spawn, args, kwargs)


    if 'parent_id' in kwargs:
        log('   spawn had an extra "parent_id" argument', kwargs)
        del kwargs['parent_id']

    # TODO:
    #
    # The returned signal (from the previous task execution)
    # should have the all_flow_results .
    # Push this to the offload task, to allow pushing back later.
    #
    # LAter:
    # At this point, capture the all_flow_results param
    # stored (somewhere) through the spawn
    afr = sig_result.all_flow_results

    # _args = getattr(sig_result, '_args', ())
    # _kwargs = getattr(sig_result, '_kwargs', {})
    _spawn_task = run_sub_task_script(
        sig_result.spawn,
        *args, **kwargs,
        parent_id=orig_task.id,
        parent_args=getattr(sig_result, '_args', ()),
        parent_kwargs=getattr(sig_result, '_kwargs', {}),
        all_flow_results=afr,
        )

    log('^  Spawn ID', _spawn_task.id)

    # add the new Task connection to the owner task(flow by task id.)
    # without a complete flag.
    flow, conn = create.flow_task_connection(orig_task, _spawn_task)
    if flow is None:
        log('x  Attemping to access flow failed due to DNI:', orig_task.id)
    else:
        log('*  Good. Spawn saved against flow.')

    return _spawn_task


def add_spawn_to_flow(task, task_job):
    # store the new spawn task to the owner flow as an ID connection
    # When the task is done - calling _post_, the parent_id is
    # this owner id, to continue a WAIT flow.
    conn = create.connection(task.id, task_job.id)
    try:
        flow_model = models.Flow.objects.get(owner=task.id)
        flow_model.spawn.add(conn)
        log('*  Good. Spawn saved against flow.')
    except models.Flow.DoesNotExist:
        log('x  Attemping to access flow failed due to DNI:', task.id)

    return conn
