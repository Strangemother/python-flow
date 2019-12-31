import importlib
from machine.log import p_blue_log
from machine.signal import Signal

log = p_blue_log('script')

def run_script(script_str, *a, **kw):
    task_class = import_task(script_str)
    # execute the external task app.
    res = task_class().perform(*a, **kw)
    if isinstance(res, Signal):
        log('decorating run_script return Signal with given params')
        log(a, kw)
        res._args = a
        res._kwargs = kw

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
    task_class = getattr(mod, class_name)
    return task_class

