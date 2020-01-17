# Tasks (Script)

The Flow machine accepts a `Task` instance to execute some code. A Task class
is a very lightweight wrapper fundamentally calling a `perform()` function.

The `machine.scripts.Task` class defines an executable resource coupled with a database `machine.models.Task`.
When creating a class based task, the flow machine will discover the file resource given to the Flow routine.

A DB task maintains a key, class import string and friendly name. The Flow will generate an discover the `scripts.Task` class using the `models.Task::string` import string.

A model:
```py
from machine import models

task_model = model.Task(name='foo', script='example.Long', key='unique-foo-long')
task_model.save()
```

The file script `example.Long` class exists in `./myapp/scripts/task_example.py::Long`:
```py
import time
from machine.scripts.task import Task

class Long(Task):
    def perform(self, *a, **kw):
        time.sleep(5)
        return True
```


## create function

The Flow machine is designed to execute a `Instance.perform()` method. To save time, generate `Task` classes to execute within a flow using strings:

```py
from machine.create import create_script, create_task
task_model = create_script('unique-foo-long', 'example.Long', 'foo')
# or
task_model = create_task(('unique-foo-long', 'example.Long',),) # all args are optional
```

As a shortcut, generate a routine of Tasks in order, using a list of task strings:

```py
from machine import create

tasks = (
    'example.Class',
    ('example.Class', )
    ('key', 'example.Class', )
    ('key', 'example.Class', 'friendly name')
    { 'key': 'key', script: 'example.Class', name:'friendly_name'}
    { 'key': 'key', script: 'example.Class',}
    { script: 'example.Class' }
    # { key: 'example.Class' }
)

db_routine = create.routine('my routine', tasks)
db_task = db.task_at(3)
# Task('key', 'example.Class', 'friendly name')

db_flow = create.flow(db_routine)
```

Execute the flow:

```py
from machine import submit_flow
run_id = submit_flow(db_flow) # or int. db_flow.pk
# == Submit flow XXX
```


## Class Based

A Task (your script) can do any code as expected. Apply to your target 'contrib'
folder in a file prefixed with `task_xxx.py`. In this example a task sleeps and
returns a dictionary for the flow machine to digest accordingly:

file `myapp/tasks/task_example.py`:

```py
import time
from machine.scripts.task import Task

class Long(Task):

    def perform(self, *a, **kw):
        log('    Perform long task,')
        time.sleep(3)
        return { 'apples': True }
```

Any standard functionality is valid. Apply argument and return any thread-safe value:

```py
class VeryLong(Task):

    def perform(self, seconds=8, *a, **kw):
        log('    Perform very long task, seconds:', seconds)
        time.sleep(seconds)
        kw['very_long'] = seconds
        return (a, kw, )
```

Although threaded, `huey` provides a great layer for execution, allowing thread-sage module scoped values. In this example we _test_ a local dictionary and spawn a `email.VeryLong` task (above) with a 7 second wait.

```py
import time
from machine.scripts.task import Task
from machine.engine import wait, spawn

cc = { 'count': 0}

class Download(Task):

    def perform(self, *a, **kw):
        log('    Pretend to download but offload the task')
        time.sleep(1)
        return spawn(
            reason='background download',
            task='email.VeryLong',
            args=(7,)
            )

    def check(self, *a, **kw):
        cc['count'] += 1
        log(f"check {cc['count']} > 10")
        return cc['count'] > 10
```

## Task Offload

You can inform the parent Flow to _wait_ without continuing for external tasks or manual intervention.

```py
import time
from machine.scripts.task import Task
from machine.engine import wait, spawn

class Offload(Task):

    def perform(self, *a, **kw):

        return wait(reason='wait for confirmation')

    def check(self, *a, **kw):
        offd = kw.get('offload')
        log(f'    Offload in check. Count: {cc["count"]}, given: "{offd}"')

        cc['count'] += 1

        time.sleep(3)

        if offd is None:
            log('    Offload return wait')
            return  wait(reason='Not Ready')
        return True
```
