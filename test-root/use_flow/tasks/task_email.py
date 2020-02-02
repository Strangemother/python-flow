import time
from machine.scripts.task import Task
from machine.engine import wait, spawn
from machine.log import p_yellow_log


log = p_yellow_log('task')

#

class Long(Task):

    def perform(self, *a, **kw):
        log('    Perform long task,')
        time.sleep(3)
        return { 'apples': True }


class VeryLong(Task):

    def perform(self, seconds=8, *a, **kw):
        log('    Perform very long task, seconds:', seconds)
        time.sleep(seconds)
        kw['very_long'] = seconds
        return (a, kw, )


class Email(Task):

    def perform(self, *a, **kw):
        """
        Return success, result
        """
        #r = wait(reason='perform reason')
        log('    Email.perform', a, kw)
        time.sleep(3)
        return { 'email_return': '@'}

    def check(self, *a, **kw):
        time.sleep(2)
        return True


cc = { 'count': 0}

class Download(Task):

    def perform(self, *a, **kw):
        log('    Pretend to download but offload the task')
        time.sleep(1)
        return spawn(
            reason='background download',
            task='email.VeryLong',
            args=(7,)
            )

    def check(self, *a, **kw):
        cc['count'] += 1
        log(f"check {cc['count']} > 10")
        return cc['count'] > 10

        # return False


class Offload(Task):

    def perform(self, *a, **kw):

        return wait(reason='wait for confirmation')

    def check(self, *a, **kw):
        offd = kw.get('offload')
        log(f'    Offload in check. Count: {cc["count"]}, given: "{offd}"')

        cc['count'] += 1

        time.sleep(3)

        if offd is None:
            log('    Offload return wait')
            return  wait(reason='Not Ready')
        return True
