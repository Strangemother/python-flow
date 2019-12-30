import time
from machine.scripts.task import Task
from machine.engine import wait, spawn


class Long(Task):

    def perform(self, *a, **kw):
        print('    Perform long task,')
        time.sleep(3)
        return {}


class VeryLong(Task):

    def perform(self, seconds=8, *a, **kw):
        print('    Perform very long task, seconds:', seconds)
        time.sleep(seconds)
        return {}



class Email(Task):

    def perform(self, *a, **kw):
        """
        Return success, result
        """
        #r = wait(reason='perform reason')
        print('    Email.perform')
        time.sleep(3)
        return {}

    def check(self, *a, **kw):
        time.sleep(2)
        return True

cc = { 'count': 0}

class Download(Task):

    def perform(self, *a, **kw):
        print('    Pretend to download but offload the task')
        time.sleep(1)
        return spawn(
            reason='background download',
            task='email.VeryLong',
            args=(20,)
            )

    def check(self, *a, **kw):
        cc['count'] += 1
        print(f"check {cc['count']} > 10")
        return cc['count'] > 10

        # return False


class Offload(Task):

    def perform(self, *a, **kw):
        return wait(reason='wait for confirmation')

    def check(self, *a, **kw):
        offd = kw.get('offload')
        print(f'    Offload in check. Count: {cc["count"]}, given: "{offd}"')

        cc['count'] += 1

        time.sleep(3)

        if offd is None:
            print('    Offload return wait')
            return wait(reason='Not Ready')
        return True
