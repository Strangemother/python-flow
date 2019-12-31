"""Functions to run the flow streams of the state machine within the context
of a django environment. Each function expects django db models.
"""
import importlib
from machine.flow import *
from machine.signal import *

from machine.log import p_red_log
log = p_red_log('engine')


def reset_flow(flow):
    flow.position = 0
    flow.state = 'INIT'
    flow.complete = False
    flow.owner = None
    flow.stores.clear()
    flow.save()


def run_all_flow(flow, *a, **kw):
    task_res_tuple = ()
    run = flow.complete is False

    if run is False:
        log('Will not run_all_flow as flow.complete is True')
        return ()

    log('  \nRun all flow.')
    while run:
        # The just ran task and its immediate result.
        task, result = run_flow_step(flow, *a, **kw)

        run = flow.complete is False
        # capture stop events here
        # and return early if required.
        # Maye flag the Flow is waiting for a task.
        if isinstance(result, Signal):
            log('  engine.run_all_flow received Signal return.')
            stop = signal_check(flow, task, result)
            run = not stop
            # edit the signal for the post-hook digest
            result.flow_result = task_res_tuple
            log('decorating the signal with loop args', a, kw)
            result._args = a
            result._kwargs = kw
            return result
        task_res_tuple += (result, )
    return task_res_tuple


def run_flow_step(flow, *a, **kw):
    """Run the flow next step.
    """
    if flow.complete:
        log('  Will not continue, flow complete')
        return

    log('  run_flow_step', flow.state)
    # At this point we can check the flow for a previous state.
    if flow.state == 'WAIT':
        log('  Flow state is WAIT, checking the existing.')
        # The last task froze the flow.
        # Perform a pickup.
        return step_check_continue_flow(flow, *a, **kw)

    return step_continue_flow(flow, *a, **kw)


def step_check_continue_flow(flow, *a, **kw):
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
    task = get_routine_task(flow.routine, flow.position)
    TaskClass = import_task(task.script)

    set_flow_check(flow)

    log('  Assert a test of the current task.', TaskClass)
    res = TaskClass().check(*a, **kw)

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

    _save_flow_and_step(flow, res, task)
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

    _save_flow_and_step(flow, res, task)
    return task, res


def _save_flow_and_step(flow, res, task):
    if hasattr(res, 'store_flow_and_step'):
        res.store_flow_and_step(flow, task)
    else:
        store_flow_and_step(flow, task, res)


def get_current_task(flow):
    return get_routine_task(flow.routine, flow.position)


def run_routine_index_task(routine, position=0, *a, **kw):
    """Run the correct Task given the routine and the current flow position.
    Return success, result and Task instance.
    """
    task = get_routine_task(routine, position)

    # if ok is False:
    #     return False, str(task), None

    res = run_task(task, *a, **kw)
    return res, task


def get_routine_task(routine, position):
    """Return the task at the given position from the given routine

        ok, task = get_routine_task(routine, 2)
    """
    tasks = ordered_tasks(routine)
    task = tasks[position]
    return task


class Signal(object):
    flow_result = None
    stop_flow = False

    def __init__(self, *a, **kw):
        self.__dict__.update(kw)

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}, {self.state} stop({self.stop_flow})'

    def store_flow_and_step(self, flow, task):
        if self.flow_result is not None:
            store_flow_and_step(flow, task, self.flow_result)


def is_stop_signal(flow, task, result):
    return result.stop_flow


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


def wait(**kw):
    r = Signal(name='wait', stop_flow=True, state='WAIT', **kw)
    return r


def spawn_result(**kw):
    r = Signal(name='spawn_result',
            stop_flow=True,
            state='WAIT',
            **kw)
    return r


def spawn(**kw):
    r = Signal(name='spawn',
            stop_flow=True,
            state='WAIT',
            spawn=kw.get('task'),
            **kw)
    return r


def get_task_attached(flow):
    task = get_routine_task(flow.routine, flow.position)
    return import_task(task.script)


def ordered_tasks(routine):
    """Given a Routine instance return a list of ordered tasks by weight
    """
    tasks = {x.key:x for x in routine.tasks.all()}
    weights = routine.weights.all().order_by('weight')
    ordered = ()
    for wo in weights:
        ordered += (tasks[wo.key],)
    return ordered


def run_task(task, *a, **kw):
    """Given a db Task instance, run the attached script as a task class,
    all given arguments are passed to the task class `perform()` method.

    Return the result of the script call
    """
    return run_script(task.script, *a, **kw)


def run_script(script_str, *a, **kw):
    task_class = import_task(script_str)
    # execute the external task app.
    res = task_class().perform(*a, **kw)
    if isinstance(res, Signal):
        log('decorating run_script return Signal with given params')
        log(a, kw)
        res._args = a
        res._kwargs = kw

    return res


def import_task(module_string):
    """Given a localised module string, import the task from the contrib space

        import_task('email.Email')
        # same as
        from machine.scripts.task_email import Email
    """
    module, class_name = module_string.split('.')
    path = f"machine.scripts.task_{module}"
    mod = importlib.import_module(path)
    task_class = getattr(mod, class_name)
    return task_class


def store_flow_and_step(flow, task, result):
    """Given a db Flow, db Task and raw result, store the result to the flow
    and _step_ the flow state to the next state.
    If the position is the end of the flow, flag 'done'
    """
    # flow.state = 'COMPLETE'
    store_task_result(flow, task, result)
    flow.position += 1
    if flow.position >= flow.routine.tasks.count():
        log('  Done.')
        set_flow_done(flow)
    flow.save()


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
