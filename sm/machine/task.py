from machine.script import run_script


def run_task(task, *a, **kw):
    """Given a db Task instance, run the attached script as a task class,
    all given arguments are passed to the task class `perform()` method.

    Return the result of the script call
    """
    return run_script(task.script, *a, **kw)


def ordered_tasks(routine):
    """Given a Routine instance return a list of ordered tasks by weight
    """
    tasks = {x.key:x for x in routine.tasks.all()}
    weights = routine.weights.all().order_by('weight')
    ordered = ()
    for wo in weights:
        ordered += (tasks[wo.key],)
    return ordered


def run_routine_index_task(routine, position=0, *a, **kw):
    """Run the correct Task given the routine and the current flow position.
    Return success, result and Task instance.
    """
    task = get_routine_task(routine, position)

    # if ok is False:
    #     return False, str(task), None

    res = run_task(task, *a, **kw)
    return res, task


def get_current_task(flow):
    return get_routine_task(flow.routine, flow.position)



def get_routine_task(routine, position):
    """Return the task at the given position from the given routine

        ok, task = get_routine_task(routine, 2)
    """
    tasks = ordered_tasks(routine)
    task = tasks[position]
    return task
