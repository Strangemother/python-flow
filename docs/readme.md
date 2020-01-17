# Flow Machine

Run many asynchronous tasks in order by creating a Flow of actions.

Flow Machine run your scripts as Tasks in sequence. As each task succeeds the next Task in your defined flow will start. Connect many tasks and flows to run your procedures. Using `django` and `huey` extend your flows to run all your functional steps.

Considered usages:

+ Authorisation flows
+ Download and digest sequences
+ create functional code style interfaces
+ Pipeline or _block-code_ development

---

Overall I want this project for myself to power the consumption of many endpoints, without writing code for each process. Using Flow Machine I develop many smaller chunks of code and apply them to usable flows.

An example may be IoT tooling for applying many small steps over a long period. Another example is data scraping and personal aggregation.

# Overview

A developer initially creates one or more Tasks applied to a Routine. When executed a Task calls the given script code and runs an accepted `contrib` located class and source. The execution of Tasks is performed in sequence maintained by a Routine.

A Flow binds a Routine and its tasks, to a requested execution and the TaskResults. As a Flow proceeds through each step the status is updated until DONE.

One or more Flow entities may be running at a given point. Each task is held is a `huey` process - therefore _process_ threaded. Given the initial input many flows can run at once.


## How it works

1. Make Tasks to run your code
2. Build Routines to run your Task
3. Run Flow to use the Tasks in order


## Task

The term 'task' may be initially ambiguous. a database Task `machine.models.Task` applies a developer given script, to a key and name. A `huey` Task is a recently thread with a unique ID and expected result. When applying User Interface work, a Task refers to the DB defined allows script to run. However nearly all the documentation references `huey` Tasks and its unique ID.

Therefore a Task is always in reference to "the thing we just submitted to the Flow Machine" unless your fidding in Django.

A Task class `machine.scripts.task.Task` provides a simple interface layer to connect your code into a Flow.


File `myapp.scripts.task_example`.


    import time
    from machine.scripts.task import Task
    class VeryLong(Task):

        def perform(self, seconds=8, *a, **kw):
            log('    Perform very long task, seconds:', seconds)
            time.sleep(seconds)
            kw['very_long'] = seconds
            return (a, kw, )


For fun this code accepts some seconds and sleeps. Within the Django Admin, You'll create a new `machine.models.Task` specially with the `script` "`email.VeryLong`".

Flow Machine will automatically utilise any file with the `task_` prefix, Loading the target class with, expecting a `perform()` method.


When you load contrib folder `approot/myapp/scripts/`, a Flow may run this task.

file:

    approot/myapp/scripts/task_example.py

Corresponds to import line:

    example.VeryLong



## Routine

A DB Routine connects many DB Tasks (and their `script` attributes) to one ordered sequence. An administrator will develop many routines to use within Flows.



## Flow

A DB Flow model binds a Routine sequence of execution and the result data from each Task and its `script`. Upon a _submit flow_ the flow state is `INIT` and sent to the `huey` queue. Upon each Task run the flow position index moved to the next task. The values are stored as a db `TaskResult`.

A Flow will start within its own thread given any arguments be the instigating code. As this occurs asynchronously the methods to submit a flow may occur from any process without blocking. All Tasks receive the arguments given to a Flow.

To run a Flow, generate a `machine.models.Flow` providing a chosen `Routine`. The submit Flow or id/pk to the machine for it to execute the tasks starting from `position` 0.

    from machine import main

    flow = models.Flow(routine=example_routine)
    flow.save()

    main.submit_flow(flow, foo='bar', other=1)





