from petroleum.task_status import TaskStatus


class Task:
    def __init__(self, name=None, **task_data):
        self.name = name
        self.next_task = None
        self.__dict__.update(task_data)

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.name)

    def get_next_task(self, **inputs):
        return self.next_task

    def _run(self, **inputs):
        if not self.is_ready(**inputs):
            task_status = TaskStatus(status=TaskStatus.WAITING, inputs=inputs)
        else:
            try:
                outputs = self.run(**inputs or {})
                if hasattr(self, 'on_complete'):
                    self.on_complete()
            except Exception as exc:
                task_status = TaskStatus(status=TaskStatus.FAILED,
                                         exception=exc,
                                         inputs=inputs)
            else:
                task_status = TaskStatus(status=TaskStatus.COMPLETED,
                                         outputs=outputs)
        return task_status

    def connect(self, task):
        self.next_task = task

    def is_ready(self, **inputs):
        return True

    def run(self, **inputs):
        pass
