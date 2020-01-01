import importlib
from machine.log import p_blue_log
from machine.signal import Signal

log = p_blue_log('script')

def run_script(script_str, *a, all_flow_results=None, **kw):
    TaskClass = import_task(script_str)
    # execute the external task app.
    res = TaskClass(all_flow_results=all_flow_results).perform(*a, **kw)
    if isinstance(res, Signal):
        log('decorating run_script return Signal with given params')
        log(a, kw)
        res._args = a
        res._kwargs = kw
        res.all_flow_results = all_flow_results
        print('== Adding all_flow_results to signal', res.name, len(all_flow_results))
        # append the 'all_flow_results' to the signal
        # for pickup later.

    return res


def import_task(module_string):
    """Given a localised module string, import the task from the contrib space

        import_task('email.Email')
        # same as
        from machine.scripts.task_email import Email
    """
    module, class_name = module_string.split('.')
    path = f"machine.scripts.task_{module}"
    mod = importlib.import_module(path)
    TaskClass = getattr(mod, class_name)
    return TaskClass

