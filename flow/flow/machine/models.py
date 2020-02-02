from django.db import models
#from flow.machine import main as engine
from flow.machine import task as task_m, flow as flow_m

class Task(models.Model):
    """A DB to script connection. A routine manages a list of tasks to
    call upon when running the flow. This Task represents how the general
    flow run system will work with the script.
    """
    # A unique key
    key = models.CharField(max_length=255)
    # A friendly name
    name = models.CharField(max_length=255)
    # The script inclusion
    script = models.TextField()
    # A huey process blocker during a Routine run.
    # blocking = models.BooleanField(default=False)

    def run(self, *a, **kw):
        res = task_m.run_task(self, *a, **kw)
        return res

    def __str__(self):
        return f'{self.key} - "{self.name}"'


class Weight(models.Model):
    key = models.CharField(max_length=255)
    weight = models.IntegerField()

    def __str__(self):
        return f'{self.key} - "{self.weight}"'


class Routine(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    weights = models.ManyToManyField(Weight)
    tasks = models.ManyToManyField(Task)

    def __str__(self):
        return f'{self.name}: {self.tasks.count()} tasks {self.weights.count()} weights'

    def ordered_tasks(self):
        """Given a Routine instance return a list of ordered tasks by weight
        """
        tasks = {x.key:x for x in self.tasks.all()}
        weights = self.weights.all().order_by('weight')
        ordered = ()
        for wo in weights:
            ordered += (tasks[wo.key],)
        return ordered

    def task_at(self, position):
        """Given a Routine instance return a list of ordered tasks by weight
        """
        tasks = {x.key:x for x in self.tasks.all()}
        weights = self.weights.all().order_by('weight').values_list('key', flat=True)
        return tasks[weights[position]]
        # ordered = ()
        # for wo in weights:
        #     ordered += (tasks[wo.key],)
        # return ordered


class TaskResult(models.Model):
    key = models.CharField(max_length=255)
    result = models.TextField()
    parent_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.key} - {self.result[0:100]}...'


class TaskError(models.Model):
    task_id = models.CharField(max_length=255)
    task_key = models.CharField(max_length=255)
    result = models.TextField()

    def __str__(self):
        return f'Error: {self.task_key} {self.task_id} - {self.result[0:100]}...'


class TaskConnection(models.Model):
    owner = models.CharField(max_length=255, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.owner} - {self.task_id}'


class Flow(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(default=0)

    spawn = models.ManyToManyField(TaskConnection, blank=True)
    stores = models.ManyToManyField(TaskResult, blank=True)
    errors = models.ManyToManyField(TaskError, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    complete = models.BooleanField(default=False)
    #post_clean = models.BooleanField(default=False)

    def get_tasks(self):
        return self.routine.ordered_tasks()

    def length(self):
        return self.routine.weights.count()

        # return len(self.get_tasks())

    def get_current_task(self):
        return self.routine.task_at(self.position)

    def add_exception(self, task_id, key, exception):
        te, c = TaskError.objects.get_or_create(
            task_id=task_id,
            task_key=key,
            result=str(exception))
        self.errors.add(te)
        return te


    def task_result_class(self):
        return TaskResult

    def run_step(self, *a, **kw):
        res = flow_m.run_flow_step(self, *a, **kw)
        return res

    def run_all(self, *a, **kw):
        res = flow_m.run_all_flow(self, *a, **kw)
        return res

    def reset(self):
        res = flow_m.reset_flow(self)
        return res

    def __str__(self):
        return f'{self.routine} - {self.position} - "{self.state}"'
