class WorkflowStatus:
    COMPLETED = 'COMPLETED'
    SUSPENDED = 'SUSPENDED'
    FAILED = 'FAILED'

    def __init__(self, status, inputs=None, outputs=None, exception=None):
        self.status = status
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.exception = exception

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.status)
