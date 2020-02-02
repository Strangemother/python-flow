---
title: "Installation"
date: 2021-10-17T14:00:45Z
draft: true
TableOfContents: true
weight: 10
---


## Download Flow

Flow is a standard python 3 application. You can install using pip:

```bash
$> pip install flow
```

or from source:

```bash
pip install git+git@github.com:strangemother/flow.git
```

To quickly check a successful installation, run _help_ on the `flow-consumer`:

```bash
$> flow-consumer -h
# ...
```

import `flow` in the python terminal:

```py
from flow.machine import engine
# -- Patching
```

The CLI may print " -- Patching" to inform you the internal database is mounted.
This is a good thig.


## Configure

The base application doesn't need configuring. By default the `flows-huey.db` will
generate in the current working directory.

### Django

The django application supports a user view for Flows, Tasks and Routines. You
can generate a Flow from the standard django admin, some built-in template views
or the CLI.

Add the `flow.machine` as an `INSTALLED_APP`:

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    # ...
    'flow.machine',
]
```

Then perform a migrate:

```bash
$> python ./manage.py migrate
```

The "consumer" starts as a seperate process.


### Consumer

The consumer manages the background processing of the running flows. It's built
on top of `huey`. All flows exist within the `flow.machine` to run your parallel
routines.

Running a consumer won't do much until we create 'Tasks'. Create a flow consumer
with 16 background workers use `--help` for more.

```bash
$> flow-consumer -w 16
```

