from genslides.task.response import ResponseTask
from genslides.task.base import TaskDescription

import os
import re


class ReadFileTask(ResponseTask):
    def __init__(self, task_info: TaskDescription, type="ReadFile") -> None:
        super().__init__(task_info, type)

    def getRichPrompt(self) -> str:
      #   return re.escape(self.prompt)
        return (self.prompt)

    def executeResponse(self):
      #   str = "J:\WorkspaceFast\genslides\examples\05table_parts_slides1_req.txt"
        param_name = "path_to_read"
        if param_name in self.params:
            self.params[param_name] = self.getRichPrompt()
        else:
            self.params.append({param_name: self.getRichPrompt()})

        if os.path.isfile(self.getRichPrompt()):
            with open(self.getRichPrompt(), 'r') as f:
                print("path_to_read =", self.getRichPrompt())
                text = f.read()
                self.msg_list.append({
                    "role": self.prompt_tag,
                    "content": text
                })
