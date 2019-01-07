from datetime import datetime
from petroleum import PetroleumObject
from petroleum.json_encoder import ToJSONMixin
from petroleum.task_status import TaskStatusEnum
from petroleum.workflow_status import WorkflowStatus
from petroluem.task_log import TaskLogEntry


class Workflow(PetroleumObject, ToJSONMixin):
    def __init__(self, start_task, id_to_task_mapper, state=None):
        self.start_task = start_task
        self.id_to_task_mapper = id_to_task_mapper
        self._init_state(state)

    def _init_state(self, state):
        self.state = state
        if not hasattr(self.state, 'task_log'):
            self.state.task_log = []
        if not hasattr(self.state, 'next_task'):
            self.state.next_task_id = self.start_task.id

    def _run_with_log(self, task, inputs):
        log_entry = TaskLogEntry(started_at=datetime.now(),
                                 id=task.id)
        self.state.task_log.append(log_entry)
        task_status = task._run(**inputs)
        log_entry._update_with_status(task_status)
        return task_status

    def _run_tasks(self, task, **inputs):
        self.current_task = task
        task_status = self._run_with_log(task, inputs)
        if task_status.status == TaskStatusEnum.COMPLETED:
            next_task = task.get_next_task(task_status)
            self.state.next_task_id = next_task.id
            if next_task is None:
                return WorkflowStatus(
                    status=WorkflowStatus.COMPLETED,
                    outputs=task_status.outputs,
                )
            else:
                return self._run_tasks(next_task, **task_status.outputs)
        elif task_status.status == TaskStatusEnum.FAILED:
            return WorkflowStatus(
                status=WorkflowStatus.FAILED, exception=task_status.exception
            )
        elif task_status.status == TaskStatusEnum.WAITING:
            return WorkflowStatus(
                status=WorkflowStatus.SUSPENDED, inputs=task_status.inputs
            )

    def _get_next_task(self):
        return self.id_to_task_mapper(self.state.next_task_id)

    def get_state(self) -> dict:
        return self.state

    def resume(self, **inputs):
        return self._run_tasks(self._get_next_task(), **inputs)
