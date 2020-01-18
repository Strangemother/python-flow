"""The create functions help generate Task, Routine and Flow models without
using simpler strings and structures.
These functions create the required database entities of which can be created
through the django admin.

    from machine import create

    create.flow()
    create.tasks()
    create.routine()
"""

from machine import models


def create_flow(routine, position=0, name=None, safe=True,):
    """
    Create a new flow instance using the given Routine and optional position.
    The routine is fetched or creaed and applied to a newly created Flow
    Return the new Flow instance
    """
    Ro = models.Routine.objects
    if isinstance(routine, int):
        # pk
        routine = Ro.get(pk=routine)
    elif isinstance(routine, str):
        # name
        routine = Ro.get(name=routine)
    elif isinstance(routine, (tuple, list)):
        routine = create_routine(name, routine, safe=safe)
    flow = models.Flow(
            routine=routine,
            position=position,
        )
    flow.save()
    return flow


def connection(owner_id, task_id):
    con = models.TaskConnection(
        owner=owner_id,
        task_id=task_id
    )
    con.save()
    return con


def flow_task_connection(task, task_job):
    # store the new spawn task to the owner flow as an ID connection
    # When the task is done - calling _post_, the parent_id is
    # this owner id, to continue a WAIT flow.
    conn = connection(task.id, task_job.id)
    try:
        flow_model = models.Flow.objects.get(owner=task.id)
        flow_model.spawn.add(conn)
        return flow_model, conn
    except models.Flow.DoesNotExist:
        return None, conn


def create_routine_tasks(name, items):
    task_models = create_tasks(items)
    keys = [x.key for x in task_models]
    return create_routine(name, keys)


def create_routine(name, scripts, safe=True):
    """Create a routine with the given name and list of task keys.
    Each key resolves a Task instance applied in-order.
    Return the newly created routine
    """
    if safe:
        tasks = models.Task.objects.filter(key__in=scripts)
    else:
        tasks = create_tasks(scripts)
    weights = tuple((i, k) for i, k in zip(range(len(scripts)), scripts))

    wms = ()
    for i, k in weights:
        wm, created = models.Weight.objects.get_or_create(key=k, weight=i)
        if created:
            wm.save()
        wms += (wm, )
    #weight_models = models.Weight.objects.bulk_create(wms)
    routine, _ = models.Routine.objects.get_or_create(
        name=name,
        )

    routine.save()
    routine.weights.add(*wms)
    routine.tasks.add(*tasks)
    #routine.save()
    return routine


def create_tasks(items):
    """Generate db model Task objects for Routine usage.
        (
            'example.Class',
            ('example.Class', )
            ('key', 'example.Class', )
            ('key', 'example.Class', 'friendly name')
            { 'key': 'key', script: 'example.Class', name:'friendly_name'}
            { 'key': 'key', script: 'example.Class',}
            { script: 'example.Class' }
            # { key: 'example.Class' }
        )
    """
    res = ()
    for item in items:
        res += (create_task(item), )
    return res


def create_task(item):
    if isinstance(item, (tuple, list)):
        task = create_script(*item)
    elif isinstance(item, dict):
        task = create_script(**item)
    elif isinstance(item, str):
        task = create_script(script=item)
    return task


def create_script(key=None, script=None, name=None):
    if key is None:
        key = script or name
    if script is None:
        script = key
    if name is None:
        name = script

    task, created = models.Task.objects.get_or_create(
        key=key,
        name=name,
        script=script
        )
    #if task.save()

    return task


flow = create_flow
tasks = create_tasks
task = create_task
routine = create_routine
routine_tasks = create_routine_tasks
script = create_script
