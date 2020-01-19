from machine.log import p_white_log
from machine.task import run_routine_index_task, get_routine_task
from machine.signal import *
# from machine.signal import Signal, signal_check, is_stop_signal
from machine.script import import_task


log = p_white_log('flow')

def set_flow_wait(flow):
    return set_flow_state(flow, 'WAIT')


def set_flow_running(flow):
    return set_flow_state(flow, 'RUNNING')



def set_flow_check(flow):
    return set_flow_state(flow, 'CHECK')



def set_flow_fail(flow):
    return set_flow_state(flow, 'FAIL')


def set_flow_done(flow):
    flow.complete = True
    return set_flow_state(flow, 'DONE')


def set_flow_state(flow, state):
    flow.state = state
    return flow.save()


def fail_flow(flow, exc, task):
    log(f'A Fatal error renders this flow a FAIL: "{flow.pk}"')
    key = flow.get_current_task().key
    flow.add_exception(task.id, key=key, exception=exc)
    set_flow_fail(flow)


def signal_check(flow, task, result):
    result.owner = flow.owner
    if is_stop_signal(flow, task, result):
        log(f'-    Stopping flow({flow}) to {result.state} because:', task.name, result.reason)
        flow.state = result.state
        #result.last = result
        flow.save()
        set_flow_state(flow, result.state)
        return True
    return False


def run_all_flow(flow, *a, **kw):
    task_res_tuple = ()
    run = flow.complete is False

    if run is False:
        log('Will not run_all_flow as flow.complete is True')
        return ()

    log('  \nRun all flow.')
    flow_results = {}

    if 'all_flow_results' in kw:
        flow_results = kw['all_flow_results']
        print('run_all_flow - Given all_flow_results.', flow_results)
        del kw['all_flow_results']

    while run:
        # The just ran task and its immediate result.
        task, result = run_flow_step(flow, *a,
                all_flow_results=flow_results, **kw)

        # (Pdb) type(task)
        # <class 'machine.models.Task'>
        run = flow.complete is False
        # capture stop events here
        # and return early if required.
        # Maye flag the Flow is waiting for a task.
        if isinstance(result, Signal):
            log('  engine.run_all_flow received Signal return.')
            stop = signal_check(flow, task, result)
            run = not stop
            # edit the signal for the post-hook digest
            #result.flow_result = task_res_tuple
            log('decorating the signal with loop args', a, kw)
            result._args = a
            result._kwargs = kw
            result.all_flow_results = flow_results
            return result
        key = task.key
        flow_results[key] = result
        task_res_tuple += (result, )
    return task_res_tuple


def store_flow_and_step(flow, task, result):
    """Given a db Flow, db Task and raw result, store the result to the flow
    and _step_ the flow state to the next state.
    If the position is the end of the flow, flag 'done'
    """
    # flow.state = 'COMPLETE'
    store_task_result(flow, task, result)
    flow.position += 1
    if flow.position >= flow.length():
        log('  Done.')
        set_flow_done(flow)
    flow.save()

store_and_step = store_flow_and_step

def store_task_result(flow, task, res):
    """Given a db Flow , db Task and raw result, save the result as a TaskResult
    and append to the flow stored data.
    """
    log('  Saving result', task.name)
    task_result = flow.task_result_class()(
        key=task.key,
        result=res
        )
    task_result.save()
    res = flow.stores.add(task_result)
    return res


def reset_flow(flow):
    flow.position = 0
    flow.state = 'INIT'
    flow.complete = False
    flow.owner = None
    flow.stores.clear()
    flow.spawn.clear()
    flow.save()


def run_flow_step(flow, *a, **kw):
    """Run the flow next step.
    """
    if flow.complete:
        log('  Will not continue, flow complete')
        return

    log('  run_flow_step', flow.state)
    # At this point we can check the flow for a previous state.
    ffs = kw.get('flow_force_step', False)
    if flow.state == 'WAIT' and (ffs is not True):
        log('  Flow state is WAIT, checking the existing.')
        # The last task froze the flow.
        # Perform a pickup.
        return step_check_continue_flow(flow, *a, **kw)

    return step_continue_flow(flow, *a, **kw)


def step_check_continue_flow(flow, *a, all_flow_results=None, **kw):
    """Reassert the current flow task by performing checks
    through the Task methods. If successful the Task asserts True,
    the flow is _stepped_ and the next task is run.

    If the task check asserts false, the flow will not step and continue,
    The state remains as the expected "WAIT" for another manual restart.

    This function is called if the `run_flow_step` detects flow.state as 'WAIT'
    """
    # check if the flow can continue given the
    # task and position.

    #TaskClass = get_task_attached(flow)

    """
    As flow is in 'WAIT', we want to check the Task of which actioned
    the step. The position is incremented when a Task runs, as such
    a 0 index pointer is the ordered task list -1.

    """
    task = get_routine_task(flow.routine, flow.position-1)
    TaskClass = import_task(task.script)

    set_flow_check(flow)

    log('  Assert a test of the current task.', TaskClass)
    res = TaskClass(all_flow_results=all_flow_results).check(*a, **kw)

    # fail_flow(flow, res, task)

    # if successful, allow a step - else store any
    # data and return for continued blocking.
    is_false = isinstance(res, bool) and (res is False)
    if is_false:
        set_flow_wait(flow)
        log('  Check returned bool "False", will not continue')
        return task, wait(reason=f'check assert ready: {not is_false}')

    if isinstance(res, Signal):
        log('  check continue received signal')
        stop = is_stop_signal(flow, task, res)
        if stop:
            log('  . Stop, storing result and not continuing index')
            set_flow_state(flow, res.state)
            store_task_result(flow, task, res)
            return task, res

    log('  check good - save flow step and continue', res)
    set_flow_running(flow)

    save_flow_result_and_step(flow, res, task)
    return task, res


def step_continue_flow(flow, *a, **kw):
    """Continue the given flow, pushing the index and running the
    next expected task in the routine.
    """
    log('  step_continue_flow')
    set_flow_running(flow)

    res, task = run_routine_index_task(
        flow.routine,
        flow.position,
        *a, **kw)

    # if ok is False:
    #     fail_flow(flow, res, task)

    save_flow_result_and_step(flow, res, task)
    return task, res


def save_flow_result_and_step(flow, res, task):
    # if hasattr(res, 'store_flow_and_step'):
    #     res.store_flow_and_step(flow, task)
    # else:
    #     store_flow_and_step(flow, task, res)
    return store_flow_and_step(flow, task, res)
