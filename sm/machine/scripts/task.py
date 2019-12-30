

class Task(object):
    """A Runnable script unit called by a db Task within a flow.
    """

    def check(self, *a, **kw):
        print('Perform check')
        return False

    def perform(self, *a, **kw):
        """Run the action
        """
        pass

