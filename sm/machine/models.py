from django.db import models
from machine import engine


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
        res = engine.run_task(self, *a, **kw)
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
        return f'{self.name}: {self.tasks.count()} tasks'


class TaskResult(models.Model):
    key = models.CharField(max_length=255)
    result = models.TextField()
    parent_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.key} - {self.result[0:100]}...'

class TaskConnection(models.Model):
    owner = models.CharField(max_length=255, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f'{self.owner} - {self.task_id}'

class Flow(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(default=0)
    stores = models.ManyToManyField(TaskResult, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    complete = models.BooleanField(default=False)

    def task_result_class(self):
        return TaskResult

    def run_step(self, *a, **kw):
        res = engine.run_flow_step(self, *a, **kw)
        return res

    def run_all(self, *a, **kw):
        res = engine.run_all_flow(self, *a, **kw)
        return res

    def reset(self):
        res = engine.reset_flow(self)
        return res

    def __str__(self):
        return f'{self.routine} - {self.position} - "{self.state}"'
