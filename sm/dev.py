#import head

from machine import main as mac
from machine.models import Flow

f = Flow.objects.first()

def reset(pk=None):
    u = f
    if pk is not None:
        u = Flow.objects.get(pk=pk)
    print('Reseting flow')
    u.reset()


def main(flow_id=3):
    print('Submitting flow to main.submit_flow', flow_id)
    #mac.submit_flow(f)
    reset(flow_id)
    mac.submit_flow(flow_id, 5, telephone='ert')

def reflow(*a, **kw):
    """Resend the flow entity.
    """
    f.refresh_from_db()
    mac.submit_flow(f, *a, **kw)

if __name__ == '__main__':
    main()
