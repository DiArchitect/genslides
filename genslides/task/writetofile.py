from genslides.task.response import ResponseTask
from genslides.task.base import TaskDescription


import os

class WriteToFileTask(ResponseTask):
    def __init__(self, task_info: TaskDescription, type="WriteToFile") -> None:
        super().__init__(task_info, type)

    def getRichPrompt(self) -> str:
        return (self.prompt)

    def executeResponse(self):
        param_name = "path_to_write"
        if param_name in self.params:
            self.params[param_name] = self.getRichPrompt()
        else:
            self.params.append({param_name: self.getRichPrompt()})

        if os.path.isfile(self.getRichPrompt()):
            with open(self.getRichPrompt(), 'w') as f:
                print("path_to_read =", self.getRichPrompt())
                text = self.msg_list[len(self.msg_list) - 1]["content"]
                f.write(text)
