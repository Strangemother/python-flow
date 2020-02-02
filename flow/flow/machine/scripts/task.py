

class Task(object):
    """A Runnable script unit called by a db Task within a flow.
    """

    def __init__(self, all_flow_results=None):
        self.all_flow_results = all_flow_results

    @property
    def flow_results(self):
        return self.all_flow_results

    def check(self, *a, **kw):
        print('Perform check', self.__class__.__name__)
        return False

    def perform(self, *a, **kw):
        """Run the action
        """
        pass

