from machine.scripts.task import Task
from machine.signal import wait, spawn
import time


class One(Task):

    def perform(self, *a, **kw):
        return { 'one': True }


class Two(Task):

    def perform(self, *a, **kw):
        return { 'two': True }


class Three(Task):

    def perform(self, *a, **kw):
        return { 'three': 10 }


class Spawn(Task):

    def perform(self, *a, **kw):
        return spawn(
            spawn_value=55,
            reason='Go get some info...',
            task='test.SpawnPerform')


class Sleep(Task):
    def perform(self, *a, **kw):
        count = kw.get('count', 3)
        print('Sleep for', count)
        time.sleep(count)
        return dict(slept=count)


class Wait(Task):

    def perform(self, *a, **kw):
        print('Run wait')
        return wait(
                reason='Wait for external'
            )


class SpawnPerform(Task):

    def perform(self, *a, **kw):
        time.sleep(15)
        kw.update({'spawn_result': 101})
        return kw


class Four(Three):

    def perform(self, *a, **kw):
        # x + 100
        return { 'four': 10 }


class Five(Four):

    def check(self, *a, **kw):
        print('== task_test.Five.check', kw, self.flow_results)
        return True


    def perform(self, *a, **kw):
        print('== task_test.Five.perform', kw)
        # x + 100
        kw['five_add'] = 938
        fr = self.flow_results
        if fr is None:
            print(' ===== Five did not have flow_results')
        kw.update(fr)
        return kw


