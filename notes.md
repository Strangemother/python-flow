A django state machine

Task:
    A model with an attached thing to run. A user will run this task to produce a result
    the result is pushed to the users flow data


Routine:
    A model recoring all the tasks to complete in a flow. user data exists in the flow

Flow:
    A coupling of a routine and a user, a flow keeps the state and data for the users process.

User:
    A Person instigating the Routine, Adding an input at each step to drive the flow


Task:
    name:   a friendly name
    script: the attached action

Routine:
    [Task]: A list of tasks to run in order. Each step is

Flow
    Routine: The routine the flow is performing
    User: The owner of the flow
    [results]: content of each step result for the flow
    state: the running state of a flow, such as 'running', or 'waiting'
    step: the int step through process for index tracking of tasks


## General flow

A django view will submit a Flow request, storing the correct initial information to a new Flow model. On succession (or manually) a 'run_flow' routine will start and continue the flow until complete.

Using Huey the task is offloaded to the consumer. A Flow consumer will manage the entire routine management with context to the database. Fundamentally task flow is monitored through the database and external pipes.

The Flow will run a Routine containing tasks. Each Task will run until complete, storing any result back into the owning flow. The huey run_flow will maintain this until death.
A Task may be 'blocking' or 'non-blocking', governing the huey task. if blocking the flow runner will instigate a task and freeze the thread until the task is complete. Considering a `while` look, the owning thread will live until the task is _done_ to proceed to the next task.

A non-blocking task is executed by the flow runner but offloads the task to another huey task. The task id is stored in the Flow and flagged as running, but waiting on an offloaded process. a post-execute hook signals the end of the huey task, of a new flow manager to continue until completion.


## Task

A Task integrates the flow with runnable scripts. The `script` block maintains the code to run, abstracted by the task runner.

The `script.task.Task` leverages methods for the API.. The `perform()` method
is called through the flow to run the as bound action. The result should be a raw value (used by the overall flow and routine) or a flag for the loop processing.

The flag will inform the flow runner to _wait_, _kill_ etc, given by the running script.


### wait

A Task may need to wait for external input, such as an email response through another Flow or external app. Return `wait()` signals the flow runner to close the running loop and mark the flow as 'WAITING'. In some course, the flow is re-initialised to check if the flow is complete.

Fundamentally a Flow is a index pointer and Routine, therefore it's easy enough to re-assert the same task or manually move a flow by changing the db `position` index value to the next int. An external app may interface with the database and store associated data and index change. django URLs can be used to push flow ints with REST API calls.

secondly a Routine is 'WAITING' the flow runner can call upon a 'check' or 'pickup' function through the `Task` api, allowing the attached script to assert is local state, checking the DB itself.


### result

The result of a Task.perform may be any picklable value such as a `dict` or `int`. Alternatively use the `result()` to clearly ensure your content is a successive value. This is also convenient for functional mapping


    class SendEmail(Task):

        def perform(self):
            if is_logged_in():
                try:
                    return True, result()
                except ConnectionError as e:
                    return False, result(error=e)

            return True, wait(reason='login_required')




### kill

A Task may fail during processing and should not continue the flow and the next steps. the `kill` defines a stop - much like `done`, but with a failure rather than a positive result.

This differs to the `success` value of a `perform()` method return tuple. A `kill` defines _the Task and script ran successfully but the result should end the flow_. A `success==False` defines _the Task script failed to execute with an error outside the flow management_

Good kill:

    class Email(Task):
        def perform(self):
            success = True
            kill_signal = kill(reason="Smoke signals preferred.")
            return success, kill_signal


Task fail:

    class Email(Task):
        def perform(self):
            try:
                result = missing_function(reason="Smoke signals preferred.")
            except NameError as e:
                result = str(e)
                success = False

            return success, result


### done

A Task may signal an early Flow completion by returning a `done()` flag. This stops the remaining tasks and marks the flow as complete.


# Issues

A Django error when executing the DB connection:

    django.db.utils.DatabaseError: DatabaseWrapper objects created in a thread can only be used in that same thread. The object with alias 'default' was created in thread id 12140 and this is thread id 48945360

A django connection is not thread-safe therefore cannot be shared across processes or greenlets. To circumvent this the main execution script `machine.main` naturally runs inside the django context. The huey interface generates django connections for threads through `on_startup`.

Therefore this error is occuring because the django environment has already been instansiated but another insantiation is occuring though another thread.

Ensure the django connection is imported once per exeuctional head. This may occur when importing the `head` and then executing `django_connect.bind()`

    from head import *
    import django_connect

    django_connect.bind()
    # DBError




