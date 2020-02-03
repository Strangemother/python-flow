"""Functions to run the flow streams of the state machine within the context
of a django environment. Each function expects django db models.
"""

from flow.machine import patch

from flow.machine.flow import *
from flow.machine import flow

from flow.machine.signal import *
# from flow.machine.routine import *
from flow.machine.script import *
from flow.machine.task import *
from flow.machine.log import p_red_log
#from flow.machine import create
from flow.machine.main import submit_flow, force_step_submit_flow, submit_create_flow
log = p_red_log('engine')

submit = submit_flow
force_step = force_step_submit_flow

# def get_task_attached(flow):
#     task = get_routine_task(flow.routine, flow.position)
#     return import_task(task.script)
