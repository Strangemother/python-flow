"""Functions to run the flow streams of the state machine within the context
of a django environment. Each function expects django db models.
"""
from machine.flow import *
from machine import flow

from machine.signal import *
# from machine.routine import *
from machine.script import *
from machine.task import *
from machine.log import p_red_log
#from machine import create
log = p_red_log('engine')


# def get_task_attached(flow):
#     task = get_routine_task(flow.routine, flow.position)
#     return import_task(task.script)
