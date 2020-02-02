from unittest import mock
from django.test import TestCase

from machine import conf
conf.patch_conf['patched'] = True

from machine import engine
from machine import models
from unittest.mock import call

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

    @mock.patch('machine.task.run_task',
        return_value=(True, 1))
    def test_full_flow(self, run_task):

        self.flow.run_all()


        self.assertEqual(run_task.call_count, self.task_count)
        # calls = [call(<Task: task_0 - "task_0">, all_flow_results=task_args),
        #     call(<Task: task_1 - "task_1">, all_flow_results=task_args),
        #     call(<Task: task_2 - "task_2">, all_flow_results=task_args),
        #     call(<Task: task_3 - "task_3">, all_flow_results=task_args)]
        task_args = {f'task_{i}': (True, 1) for i in range(self.task_count)}
        cl = run_task.call_args_list

        for i, (args, kwargs) in zip(range(len(cl)), cl):
            task = args[0]
            expected_kwargs = {'all_flow_results': task_args}
            self.assertEqual(task.key, f'task_{i}')
            self.assertEqual(kwargs, expected_kwargs)
