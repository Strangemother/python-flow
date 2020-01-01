from machine.scripts.task import Task


class One(Task):

    def perform(self, *a, **kw):
        return { 'apples': True }


class Two(Task):

    def perform(self, *a, **kw):
        return { 'pears': True }


class Three(Task):

    def perform(self, *a, **kw):
        return { 'eggs': 10 }


class Four(Three):
    def perform(self, *a, **kw):
        x + 100
        return { 'eggs': 10 }



class Five(Four):
    pass
