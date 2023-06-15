from genslides.task.text import TextTask
from genslides.task.base import TaskDescription
import pprint
from genslides.utils.largetext import SimpleChatGPT



class ResponseTask(TextTask):
    def __init__(self, task_info : TaskDescription, type = "Response") -> None:
        super().__init__(task_info, type)


        tmp_msg_list = self.msg_list.copy()
        msg_list_from_file = self.getResponseFromFile(tmp_msg_list)
        del tmp_msg_list
        # print("Response\n==================>>>>>>>>>>>\n", pprint.pformat( self.msg_list))


        

        if len(msg_list_from_file) == 0:
            self.setChatPram("temperature")
            self.setChatPram("model")
            if self.is_freeze:
                model_name = self.getParam("model")
                chat = SimpleChatGPT(model_name=model_name)
                self.msg_list.append({"role": chat.getAssistTag(), "content": ""})
            else:
                self.executeResponse()
        else:
            # print("t=",temperature)
            if not self.getParam("model"):
                model_name =  self.reqhelper.getValue(self.type, "model")
                if model_name:
                    self.updateParam("model", model_name)
                else:
                    self.updateParam("model", "gpt-3.5-turbo")

            self.msg_list = msg_list_from_file
            print("Get list from file=", self.path)
        print("name=", self.getName())
        print("path=", self.path)
        self.saveJsonToFile(self.msg_list)

    def setChatPram(self, name):
            temperature =  self.reqhelper.getValue(self.type, name)
            print("t=",temperature)
            if temperature:
                self.updateParam(name, temperature)
 
    def executeResponse(self):
        model_name = self.getParam("model")

        print("Exe resp with model=", model_name)
        chat = SimpleChatGPT(model_name=model_name)
        temp = self.getParam("temperature")
        print("temp=", temp)
        if temp:
            chat.setTemperature(temp)
        res, out = chat.recvRespFromMsgList(self.msg_list)
        if res:
            # print("out=", out)
            pair = {}
            pair["role"] = chat.getAssistTag()
            pair["content"] = out
            self.msg_list.append(pair)



    def update(self, input : TaskDescription = None):
        stopped = self.getParam("stopped")
        if stopped:
            print("Stopped=", self.getName())
            return "",self.prompt_tag,""
        
        if self.is_freeze and self.parent:
            print("frozen=",self.getName())
            if not self.parent.is_freeze:
                self.is_freeze = False
                tmp_msg_list = self.parent.msg_list.copy()
                # print(pprint.pformat(tmp_msg_list))
                msg_list_from_file = self.getResponseFromFile(tmp_msg_list)
                if len(msg_list_from_file):
                    print("I loaded")
                    self.msg_list = msg_list_from_file

            else:
                return "","user",""
        
       

        print("Update response task=", self.getName())
        # print("Response\n==================>>>>>>>>>>>\n", pprint.pformat( self.msg_list))
        if self.parent:
            trg_list = self.parent.msg_list.copy()
        else:
            trg_list = []
        if len(self.msg_list) == 0:
            self.executeResponse()
            self.saveJsonToFile(self.msg_list)
        else:
            last = self.msg_list[- 1]
            trg_list.append(last)
            if self.msg_list != trg_list:
                trg_list.pop()
                self.msg_list = trg_list.copy()
                self.executeResponse()
                self.saveJsonToFile(self.msg_list)
        super().update(input)
        if len(self.msg_list) == 0:
            return "","user",""
        out = self.msg_list[len(self.msg_list) - 1]
        return "", out["role"],out["content"]

    def getMsgInfo(self):
        if len(self.msg_list):
            out = self.msg_list[len(self.msg_list) - 1]
            return "", out["role"],out["content"]
        return "","user",""
    
