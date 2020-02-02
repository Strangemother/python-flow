from huey import SqliteHuey
import head


count = {'val': 100}

huey = SqliteHuey(filename='huey.db')

@huey.task()
def add(a):
    count['val'] += a
    return count['val']

@huey.task()
def value():
    return count['val']



@huey.task()
def reset():
    count['val'] = 0
    return count['val']
