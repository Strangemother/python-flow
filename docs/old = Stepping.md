# How it Steps...

One main aspect of the flow machine is the _Stepping_ through tasks in a routine. In general this can become a complex challenge, so hopefully this article demystifies the internal workings.

A quick recap:

+ A Task is a script to run "example.LongWait"
+ A Routine contains many Tasks in order
+ A Flow couples a _run_ of a routine with the transient result data

When a Task is complete, the Flow index is incremented by `1`. When the index is greater than the count of tasks, the Flow is `complete`. If a Flow receives a `WAIT`/`SPAWN`, (or any `STOP` `signal`) command will not step to the next Task. An _external force_ should push the flow to continue.

```py
flow >>   run_flow_step INIT
flow >>   step_continue_flow
flow >>   Saving result test.One
flow >>   run_flow_step RUNNING
flow >>   step_continue_flow
flow >>   Saving result test.Two
flow >>   run_flow_step RUNNING
flow >>   step_continue_flow
```


## Auto Stepping

A Flow will step through a `Routine` list of `Task` items until exhausted. The flow has an `INIT` index of `0`. When the index is greater than the count of `Task` items within the ordered routine, the Flow is marked `COMPLETE`.

A Flow will attempt to continue after every successful Task completion. The new Task is instigated immediately on the same process or thread, receiving the same Flow instance. If a value from a `Task` is a `signal` type, the Flow may pause in `WAIT` or `SPAWN` phase.

In all circumstances a _pause_ will kill the current running Flow at the current index - such as `3`. If a Flow is restarted, it will continue from the same index, ignoring the previous tasks.

If the signal spawned another Task with a `signal.SPAWN` - the flow will restart after the completion of the disconnected task. The spawned task is ran outside the Flow context, and does not apply to the Routine Task list the Flow already owns.

If a Task returns a `WAIT` command, the flow must be pushed manually.


## Wait and Spawn

A Flow may pause for a range of reasons and is designed to _restart_ as required. Some signals force a pause, such as a `WAIT`. At this point the flow must be _externally forced_ to continue processing its Routine.

In a task we can return a `machine.signal.wait` type, telling the Flow `STOP`, and informing the status with a `reason` for the `WAIT` state:

```py
class Offload(Task):
    def perform(self, *a, **kw):
        return wait(reason='wait for confirmation')
```

The Flow loop will stop when it receives the `wait()` signal. At this point you can attempt to restart a flow by calling `machine.submit_flow(id)`. As the Flow index is _this task_, and the Flow is in `WAIT` status, the Flow will continue.

```py
items = (
    'test.One',
    'test.Two',
    'test.Wait',
    'test.Three',
)
flow = create.flow(items, safe=False, name='egg')
flow.get_tasks()
```

```bash
# ... snip ...
flow >> -    Stopping flow(egg: 4 tasks - 3 - "RUNNING") to WAIT because: test.Wait Wait for external
flow >> decorating the signal with loop args () {}
[2020-01-18 04:14:24,783] INFO:huey:DummyThread-2:machine.main.run_flow: 8fd8bffb-be0c-460e-8cde-d4ab14620ce4 executed in 0.190s
main >> !! Task complete machine.main.run_flow: 8fd8bffb-be0c-460e-8cde-d4ab14620ce4
 Signal wait, WAIT stop(True)
main >> !! Will not continue because stop_flow is True
 Signal wait, WAIT stop(True)
main >> x  Signal has no spawn "signal.spawn" Signal wait, WAIT stop(True)
```

Attempting to re-submit the Flow will not step the task due to no logical evaluation:

```py
flow_id = flow.pk
# previous run
mac.submit_flow(flow_id)
'8fd8bffb-be0c-460e-8cde-d4ab14620ce4'
# ...WAIT

# re-submit
>>> mac.submit_flow(flow_id)
'84b6cf84-cb87-4367-b981-52ab0f456107'
```


```bash
# re-submit logs
[2020-01-18 04:16:21,053] Executing machine.main.run_flow: 84b6cf84-cb87-4367-b981-52ab0f456107
main >> + Task egg () {}

flow >>
Run all flow.
flow >>   run_flow_step WAIT
flow >>   Flow state is WAIT, checking the existing.
flow >>   Assert a test of the current task. <class 'machine.scripts.task_test.Wait'>
Perform check Wait
flow >>   Check returned bool "False", will not continue
flow >>   engine.run_all_flow received Signal return.
flow >> -    Stopping flow(egg: 4 tasks - 3 - "WAIT") to WAIT because: test.Wait check assert ready: False
flow >> decorating the signal with loop args () {}

[2020-01-18 04:28:49,197] INFO:huey:DummyThread-1:machine.main.run_flow: 30c4e415-3a4c-42a5-a63b-f74ea290ed45 executed in 11.000s
main >> !! Task complete machine.main.run_flow: 30c4e415-3a4c-42a5-a63b-f74ea290ed45
 Signal wait, WAIT stop(True)
main >> !! Will not continue because stop_flow is True
 Signal wait, WAIT stop(True)
main >> x  Signal has no spawn "signal.spawn" Signal wait, WAIT stop(True)
```


## Pushing a Flow

You can manually force a flow to continue past the WAIT state, by changing the Flow stored values. This allows you to edit the flow state through _external_ resources, such as a callback from a REST API.

Django model edit:

```py
from machine import models, submit_flow

flow = models.Flow.objects.get(pk=69)
flow.position += 1
flow.state = 'SOMETHING' # Anything but the 'WAIT' special attribute.
flow.save()

run_id = submit_flow(flow)
```

Or use the built-in force function, applying some value as the store result
for the Task

```py
import machine
run_id = machine.force_step_submit_flow(69, foo='bar')
```


