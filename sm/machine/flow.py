
def set_flow_wait(flow):
    return set_flow_state(flow, 'WAIT')



def set_flow_running(flow):
    return set_flow_state(flow, 'RUNNING')



def set_flow_check(flow):
    return set_flow_state(flow, 'CHECK')



def set_flow_fail(flow):
    return set_flow_state(flow, 'FAIL')



def set_flow_done(flow):
    flow.complete = True
    return set_flow_state(flow, 'DONE')


def set_flow_state(flow, state):
    flow.state = state
    return flow.save()

def fail_flow(flow, res, task):
    set_flow_fail(flow)
