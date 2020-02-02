import os


patch_conf = { 'patched': False }


ROOT = os.getcwd()
#ROOT = os.path.abspath(os.path.dirname(__file__))
TASK_DB_NAME = 'flows-huey.db'

TASK_DIRS = [
    'flow.machine.scripts',
]

def get_task_db_path():
    return os.path.join(ROOT, TASK_DB_NAME)


def no_patch():
    patch_conf['patched'] = True
