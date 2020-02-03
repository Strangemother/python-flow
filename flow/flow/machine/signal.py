# from machine.flow import store_flow_and_step


class Signal(object):
    flow_result = None
    stop_flow = False

    def __init__(self, *a, **kw):
        self.__dict__.update(kw)

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}, {self.state} stop({self.stop_flow})'

    # def store_flow_and_step(self, flow, task):
    #     if self.flow_result is not None:
    #         store_flow_and_step(flow, task, self.flow_result)


def is_stop_signal(flow, task, result):
    return result.stop_flow


def wait(**kw):
    r = Signal(name='wait',
        stop_flow=True,
        state='WAIT',
        **kw)
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
        state='SPAWN',
        spawn=kw.get('task'),
        flow_routine=kw.get('routine'),
        **kw)
    return r

