from unittest import mock
from django.test import TestCase
from machine import engine
from machine import models


class FlowTestCase(TestCase):
    task_count = 4

    def setUp(self):
        #Flow.objects.create()
        for i in range(self.task_count):
            models.Task.objects.create(
                key=f'task_{i}',
                name=f'task_{i}',
                script=f'test.Task',
                )
            models.Weight.objects.create(
                key=f'task_{i}',
                weight=i,
                )
        self.routine = r = models.Routine.objects.create(
            name='Test Routine',
            )
        r.weights.set(models.Weight.objects.all())
        r.tasks.set(models.Task.objects.all())

        self.flow = models.Flow.objects.create(
            routine=r,
            owner='test',
        )

    @mock.patch('machine.engine.run_task',
        return_value=(True, 1))
    def test_full_flow(self, run_task):
        self.flow.run_all()
        self.assertEqual(
            run_task.call_count, self.task_count
        )

