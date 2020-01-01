from gevent import monkey; monkey.patch_all()
from huey import SqliteHuey

huey = SqliteHuey(filename='abba.db')


def main():
    print('main')
    #mac.submit_flow(f)
    # reset(flow_id)
    # mac.submit_flow(flow_id, 5, telephone='ert')

    pipe = (fib.s(1)
            .then(fib)
            .then(fib)
            .then(fib))


    results = huey.enqueue(pipe)
    return results(True)


@huey.task()
def fib(a, b=1):
    a, b = a + b, a
    return (a, b)  # returns tuple, which is passed as *args


@huey.post_execute()
def post_execute_hook(task, task_value, exc):
    # Post-execute hooks are passed the task, the return value (if the task
    # succeeded), and the exception (if one occurred).
    print('Task complete', task)
    # v = vv.report(10)


if __name__ == '__main__':
    r = main()

