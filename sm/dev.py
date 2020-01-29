#import head

#from machine import main as mac
from machine import engine
from machine.models import Flow

f = Flow.objects.first()

def reset(pk=None):
    u = f
    if pk is not None:
        u = Flow.objects.get(pk=pk)
    print('Reseting flow')
    u.reset()


def new_flow():
    routine = ('very_long',
               'download',
               'send_text',)
    flow, fid = mac.submit_new_flow(routine, 'new_flow')
    print('Submitted')


def main(flow_id=69):

    key = 74
    # flow = create_sleepy_flow()
    print('Submitting flow', key)
    reset(key)
    engine.submit(key)
    #mac.submit_flow(flow_id)
    #return sleep_flow()
    #mac.submit_flow(f)
    # reset(flow_id)
    # mac.submit_flow(flow_id, 5, telephone='ert')
    # crtf()

def crt():
    """
        v = crt()
        f = mac.create.flow(v)
        <Flow: bob: 4 tasks - 0 - "None">

        mac.submit_flow
        <function submit_flow at 0x0000000004F2EB70>

        mac.submit_flow(f)
        'b2ade392-b7f5-401f-913e-00d5500da42d'
    """
    items = (
        'very.Spotty',
        'wake.Ohio',
        'being.Singing',
        'talk.Twice',
        )
    return mac.create.routine_tasks('bob', items)


from machine import create


def create_sleepy_flow():
    items = (
        'test.Sleep',
        'test.Sleep',
        'test.Sleep',
        'test.Sleep',
    )

    # pk == 72
    return create.flow(items, safe=False, name='asleepy')


def sleep_flow():
    items = (
        'test.One',
        'test.Two',
        'test.Wait',
        'test.Three',
    )
    flow = create.flow(items, safe=False)
    mac.submit_flow(flow)
    return flow


def crtf():
    # routine, tasks, flow.
    items = (
        'test.One',
        'test.Two',
        'test.Three',
        'test.Spawn',
        'test.Four',
        'test.Five',
        )
    routine = mac.create.routine_tasks('crtf', items)
    flow = mac.create.flow(routine,)
    res = mac.submit_flow(flow, egg=2)
    print('CRTF Result', res)

    #mac.submit_create_flow(flow, egg=2)

def reflow(*a, **kw):
    """Resend the flow entity.
    """
    f.refresh_from_db()
    mac.submit_flow(f, *a, **kw)

if __name__ == '__main__':
    main()
