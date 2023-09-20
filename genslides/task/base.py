import genslides.utils.reqhelper as ReqHelper
import genslides.utils.request as Requester

from genslides.commands.create import CreateCommand
from genslides.helpers.singleton import Singleton

import os
from os import listdir
from os.path import isfile, join

import json

from genslides.utils.largetext import SimpleChatGPT

class TaskManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.task_id = 0
        self.task_list = []
        self.model_list = []
        chat = SimpleChatGPT()
        self.model_list = chat.getModelNames()

    def getId(self, task) -> int:
        id = self.task_id
        self.task_id += 1
        if task not in self.task_list:
            self.task_list.append(task)
        return id
    
    def getPath(self) -> str:
        if not os.path.exists("saved"):
            os.makedirs("saved")
        return "saved/"
    
    def getLinks(self):
        mypath = self.getPath()
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        out = []
        for filename in onlyfiles:
            path = join(mypath,filename)
            try:
                with open(path, 'r') as f:
                    rq = json.load(f)
                if 'linked' in rq:

                    pair = {}
                    pair['name'] = filename.split('.')[0]
                    pair['linked'] = rq['linked']
                    out.append(pair)
            except Exception as e:
                pass
        return out

    
    def getParentTaskPrompts(self):
        mypath = self.getPath()
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        out = []
        for filename in onlyfiles:
            path = join(mypath,filename)
            try:
                with open(path, 'r') as f:
                    rq = json.load(f)
                if 'parent' in rq:
                    print(path)
                    parent_path = rq['parent']
                    if parent_path == "" and 'chat' in rq and 'type' in rq:
                        print(path)
                        
                        for elem in rq['chat']:
                            if elem['role'] == 'user':
                                pair = {
                                'type' : rq['type'],
                                'content' : elem['content']
                                }
                                out.append(pair)
            except Exception as e:
                pass
        return out

    def getTaskPrompts(self, trg_path = ""):
        mypath = self.getPath()
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        out = []
        for filename in onlyfiles:
            path = join(mypath,filename)
            try:
                with open(path, 'r') as f:
                    rq = json.load(f)
                if 'parent' in rq:
                    # print(path)

                    parent_path = rq['parent']
                    if parent_path == trg_path and 'chat' in rq and 'type' in rq:
                        print("Get propmt from=",path)
                        # if rq['type'].endswith("RichText") or rq['type'].endswith("Response"):
                        if len(rq['chat']) == 0:
                            elem = {'role': 'user','content': ''}
                        else:
                            if rq['type'] == "RichText":
                                elem = rq['chat'].pop()
                            elem = rq['chat'].pop()
                        pair = {}
                        # pair['type'] = rq['type']
                        pair['type'] =filename.split('.')[0] 
                        pair['content'] = elem['content']
                        pair['role'] = elem['role']

                        out.append(pair)
                        
                        # for elem in rq['chat']:
                        #     if elem['role'] == 'user':
                        #         pair = {}
                        #         pair['type'] = rq['type']
                        #         pair['content'] = elem['content']
                        #         out.append(pair)
            except json.decoder.JSONDecodeError as e:
                print("Get json error on task prompts=", e)
            except Exception as e:
                print("Task prompts error=", type(e))
        return out




class TaskDescription():
    def __init__(self, prompt = "", method = None, parent=None, helper=None, requester=None, target=None, id = 0, type = "", prompt_tag = "user", filename = "", enabled = False, params = [], manual = False, stepped = False) -> None:
        self.prompt = prompt
        self.prompt_tag = prompt_tag
        self.method = method
        self.parent = parent
        self.helper = helper
        self.requester = requester
        self.target = target
        self.id = id
        self.type = type
        self.filename = filename
        self.enabled = enabled
        self.params = params
        self.manual = manual
        self.stepped = stepped

class BaseTask():
    def __init__(self, task_info : TaskDescription, type = 'None') -> None:
        self.childs = []
        self.is_solved = False
        self.reqhelper = task_info.helper
        self.requester = task_info.requester
        self.crtasklist = []

        type = task_info.type
        self.type = type
        self.init = self.reqhelper.getInit(type)
        self.endi = self.reqhelper.getEndi(type)

        self.prompt = task_info.prompt
        self.prompt_tag = task_info.prompt_tag
        
        self.method = task_info.method
        task_manager = TaskManager()
        self.id = task_manager.getId(self)
        request = self.init + self.prompt + self.endi
        self.task_description = "Task type = " + self.type + "\nRequest:\n" + request
        self.task_creation_result = "Results of task creation:\n"

        self.parent = task_info.parent
        self.is_freeze = False
        if  self.parent:
            self.parent.addChild(self)
            if self.parent.is_freeze:
                self.is_freeze = True
        self.target = task_info.target
        self.filename = task_info.filename

        self.affect_to_ext_list = []
        self.by_ext_affected_list = []
        self.name = self.type + str(self.id)
        self.queue = []
    
    
    def freezeTask(self):
        self.is_freeze = True
        # self.update()

    def unfreezeTask(self):
        self.is_freeze = False
        # self.update()

    def getRichPrompt(self) -> str:
        out = self.prompt
        if not out.startswith(self.init):
            out = self.init + out
        if not out.endswith(self.endi):
            out += self.endi
        for task in self.by_ext_affected_list:
            out += " " + task.prompt
        return out
    
    def getJson(self):
        return None
    

    def getIdStr(self) -> str:
        return str(self.id)
    
    def getName(self) -> str:
        return self.name
    
    def getType(self) -> str:
        return self.type

    def isInputTask(self):
        return True
    
    def getTree(self):
        par = self
        index = 0
        while(index < 1000):
            if par.parent:
                par = par.parent
            else:
                break
            index += 1
        out = par.getAllChildChains()
        return out


 
    def getAllChildChains(self):
        index = 0
        out = [self]
        trgs = [self]
        while(index < 1000):
            n_trgs = []
            found = False
            for trg in trgs:
                for ch in trg.childs:
                    found = True
                    n_trgs.append(ch)
                    out.append(ch)
            if not found:
                break
            trgs = n_trgs
            index += 1
        return out
    
    def getChainBeforeBranching(self):
        out = self.getAllChildChains()
        par = self
        index = 0
        while(index < 1000):
            if par.parent and len(par.parent.childs) == 1:
                par = par.parent
                out.append(par)
            else:
                break
            index += 1
        return out

    def getAncestorByName(self, trg_name):
        index = 0
        task = self
        while(index < 1000):
            if  task.parent != None:
                if task.parent.getName() != trg_name:
                    task = task.parent
                else:
                    return task.parent
            else:
                break
            index += 1
        return None

    def getNewID(self) -> int:
        task_manager = TaskManager()
        self.id = task_manager.getId(self)
        return self.id


    def addChildToCrList(self, task : TaskDescription):
        self.crtasklist.append(task)

    def isSolved(self):
        return self.is_solved
    
    def checkChilds(self):
        for child in self.childs:
            if not child.isSolved():
                return False
        return True

    def getChildQueuePack(self, child) ->dict:
        return { "pt":child, "type":"child","used":False}

    def addChild(self, child):
        if child not in self.childs:
            self.childs.append(child)
            self.queue.append(self.getChildQueuePack())
    
    def removeChild(self,child):
        if child in self.childs:
            self.childs.remove(child)
            self.queue.remove(self.getChildQueuePack())

    def getLinkQueuePack(self, info: TaskDescription) -> dict:
        return { "id":info.id,"method":info.method,"pt":info.target, "type":"link","used":False}

    def setLinkToTask(self, info : TaskDescription) -> None:
        self.affect_to_ext_list.append(info)
        self.queue.append(self.getLinkQueuePack())

    def resetLinkToTask(self, info : TaskDescription) -> None:
        self.affect_to_ext_list.remove(info)
        self.queue.remove(self.getLinkQueuePack())

    def getChilds(self):
        return self.childs

    def getCmd(self):
        if len(self.crtasklist) > 0:
            task = self.crtasklist.pop()
            print('Register command:' + str(task.method))
            return CreateCommand( task)
        return None
    
    def stdProcessUnFreeze(self, input=None):
            if self.parent:
                self.is_freeze = self.parent.is_freeze
            else:
                pass

    def updateIternal(self, input : TaskDescription = None):
        pass
   
    def update(self, input : TaskDescription = None):
        self.stdProcessUnFreeze(input)

       
        print("Update=",self.getName(), "|frozen=", self.is_freeze, "||")
        self.updateIternal(input)

        if input and not input.stepped:
            
            self.useLinksToTask()

            for child in self.childs:
                child.update()
        else:
            self.setupQueue()

        return "","",""
    
    def setupQueue(self):
        if self.queue and not self.isQueueComplete():
            pass
        else:
            print("Setup queue:",self.queue)

    def useLinksToTask(self):
        input = TaskDescription(prompt=self.prompt, parent=self)
        for task in self.affect_to_ext_list:
            input.id = task.id
            task.method(input)


    def resetTreeQueue(self):
        trgs = [self]
        index = 0
        while(index < 1000):
            n_trgs = []
            for trg in trgs:
                trg.resetQueue()
                for ch in trg.childs:
                    n_trgs.append(ch)
            trgs = n_trgs
            index += 1

    def resetQueue(self):
        if self.queue:
            for info in self.queue:
                info["used"] = False

    def findNextFromQueue(self):
        # print("Search for next from queue")
        if self.queue:
            for info in self.queue:
                if info["type"] == "child" and info["used"] == False:
                    # info["pt"].update(TaskDescription(stepped=True))
                    info["used"] = True
                    return info["pt"]
                if info["type"] == "link" and info["used"] == False:
                    input = TaskDescription(prompt=self.prompt, id=info["id"], stepped=True, parent=self, enabled= not self.is_freeze)
                    info["method"](input)
                    info["used"] = True
                    return info["pt"]
        return None
    
    def isQueueComplete(self):
        if len(self.queue) > 0:
            return False
        return True

    def getNextFromQueue(self):
        print("Get next from",self.getName(),"queue")
        res = self.findNextFromQueue()
        if res:
            return res
        if self.isQueueComplete():
            return self.getNextFromQueueRe()
        return None
        
    def getNextFromQueueRe(self):
        print("Get recursevly")
        trg = self
        index = 0
        while(index < 1000):
            if trg.parent is None:
                return trg
            else:
                trg = trg.parent
                res = trg.findNextFromQueue()
                if res:
                    return res
            index +=1
        return None   
    
    def getMsgInfo(self):
        return "","",""
    
    def getInfo(self, short = True) -> str:
        return "Some description"


    def beforeRemove(self):
        if self.parent:
            self.parent.removeChild(self)
        for child in self.childs:
            child.whenParentRemoved()

    def whenParentRemoved(self):
        self.parent = None

    def removeParent(self):
         if self.parent:
            self.parent.removeChild(self)
            self.parent = None
       

    def getCountPrice(self):
        return 0,0
    
    def affectedTaskCallback(self, input : TaskDescription):
        pass

    def createLinkToTask(self, task) -> TaskDescription:
        pass
        # id = len(self.by_ext_affected_list)
        # out = TaskDescription(method=self.affectedTaskCallback, id=id, parent=task )
        # self.by_ext_affected_list.append(out)
        # task.setLinkToTask(out)
        # return out
    
    def removeLinkToTask(self):
        while len(self.by_ext_affected_list) > 0:
            input = self.by_ext_affected_list.pop()
            input.parent.resetLinkToTask(input)
        
    

    def completeTask(self) -> bool:
        # print(self.getName(),"=Complete Task")
        return False 
    
    def getParam(self, param_name):
        return None
    
    def getParamList(self):
        return None
    def updateParamStruct(self, param_name, key,val):
        pass

    def getParamStruct(self, param_name):
        return False, None
    
    def getAllParams(self):
        return ""
    
    def getMsgs(self, except_task = []):
        return None
 