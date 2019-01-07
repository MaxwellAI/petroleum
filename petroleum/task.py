from petroleum import PetroleumObject
from petroleum.json_encoder import ToJSONMixin
from petroleum.task_status import TaskStatus, TaskStatusEnum


class Task(PetroleumObject, ToJSONMixin):
    def __init__(self, name=None, **task_data):
        self._name = name
        self._next_task = None
        self.__dict__.update(task_data)

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self._name)

    def _run(self, **inputs):
        if not self.is_ready(**inputs):
            return TaskStatus(status=TaskStatusEnum.WAITING, inputs=inputs)
        try:
            outputs = self.run(**inputs)
        except Exception as exc:
            return TaskStatus(
                status=TaskStatusEnum.FAILED, exception=exc, inputs=inputs
            )
        task_result = TaskStatus(
            status=TaskStatusEnum.COMPLETED, inputs=inputs, outputs=outputs
        )
        self.on_complete(task_result)
        return task_result

    def connect(self, task):
        self._next_task = task

    def get_next_task(self, task_status):
        return self._next_task

    def is_ready(self, **inputs):
        return True

    def on_complete(self, task_result):
        pass

    def run(self, **inputs):
        raise NotImplementedError()
