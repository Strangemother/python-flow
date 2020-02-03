# Flows

Run your code as a sequence of ordered tasks. Run many asynchronous tasks in order by creating a Flow of actions.

Flow Machine run your scripts as Tasks in sequence. As each task succeeds the next Task in your defined flow will start. Connect many tasks and flows to run your procedures.

Main dependencies:

+ Django
+ huey


## ELI5

Generally code has a sequence of tasks to run in order, optionally providing variables of the running code. Flows allows you to create single executable tasks and combine them as a 'Routine' to run. Then reuse the Routine as a Flow. Like this:
