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
        self.name = self.type + str(self.id)
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
    
    def setName(self, name : str):
        old_name = self.name
        self.name = name
        print("My new name is", self.name,", was", old_name)

        if self.parent:
            self.parent.updateNameQueue(old_name, name)

        for info in self.by_ext_affected_list:
            info.parent.updateNameQueue(old_name, name)

        

    
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
        if self.getName() == trg_name:
            return self
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

    def getDefCond(self) -> dict:
        return {"cond" : "None", "cur": "None", "trg": "used", "str": "None"}

    def getChildQueuePack(self, child) ->dict:
        val = {  "type":"child", "used":False ,"name": child.getName()}
        val.update(self.getDefCond())
        return val

    def getLinkQueuePack(self, info: TaskDescription) -> dict:
        return { "name": info.target.getName(), "id":info.id,"method":info.method, "type":"link","used":False}.update(self.getDefCond())
    
    def getJsonQueue(self, pack : dict) -> dict:
        if not pack:
            return {}
        if pack["type"] == "child" or pack["type"] == "link":
            # print("val:",pack)
            # if "name" not in pack:
            #     pack["name"] = val.getName()
            return pack
        return {}

    def addChild(self, child) -> bool:
        if child not in self.childs:
            self.childs.append(child)
            info = self.getChildQueuePack(child)
            self.onQueueReset(info)
            self.queue.append(info)
            return True
        return False
    
    def getChildByName(self, child_name):
        for ch in self.getChilds():
            if ch.getName() == child_name:
                return ch
            
    def getLinkedByName(self, linked_name):
        for info in self.affect_to_ext_list:
            if info.target.getName() == linked_name:
                return info.target
    
    def removeChild(self,child):
        if child in self.childs:
            self.childs.remove(child)
            self.queue.remove(self.getChildQueuePack(child))


    def setLinkToTask(self, info : TaskDescription) -> bool:
        self.affect_to_ext_list.append(info)
        info1 = self.getLinkQueuePack(info)
        self.onQueueReset(info1)
        self.queue.append(info1)
        return True

    def resetLinkToTask(self, info : TaskDescription) -> None:
        self.affect_to_ext_list.remove(info)
        self.queue.remove(self.getLinkQueuePack(info))

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

    def updateNameQueue(self, old_name : str, new_name : str):
        pass

    def resetQueue(self):
        if self.queue:
            for info in self.queue:
                self.onQueueReset(info)
    
    def onQueueReset(self, info):
        info["used"] = False
        info["cur"] = info["str"]

    def onQueueCheck(self, param) -> bool:
        # print("React on condition:",param)
        if param['cond'] == '=':
            if isinstance(param['cur'], str):
                if self.findKeyParam( param['cur']) != param['trg']:
                    return False
        elif isinstance(param['trg'], int) and isinstance(param['cur'], int):
            cur = int(param['cur'])
            trg = int(param['trg'])
            if param['cond'] == '>' and cur < trg:
                return False
            elif param['cond'] == '<' and cur > trg:
                return False
            elif param['cond'] == '=' and cur != trg:
                return False
        elif param['cond'] == 'None':
            if param['cur'] == param['trg']:
                return False
            else:
                param['cur'] = "used"
        if param['cond'] == 'for':
            print('here')
            try:
                jp = json.loads(self.getAncestorByName(param['target']).getLastMsgContent())
                if not "data" in param:
                    param['data'] = jp['data']
                    param['value'] = param['data'][0]
                    param['trg'] = len(param['data'])
                    param['cur'] = 0
                    param['str'] = 0
                else:
                    if jp['data'] != param['data']:
                        param['value'] = param['data'][0]
                        param['trg'] = len(param['data'])
                        param['cur'] = 0
                        param['str'] = 0
                    else:
                    # print(param)
                        index = param['cur'] + 1
                        param['value'] = param['data'][index]
                        param['cur'] = index
                    # print(param)
                # else:
                    # return False
            except Exception as e:
                print("Some go wrong:", e)
                return False
        print("React on condition:",param)
        param["used"] = True
        return True
    

    def syncQueueToParam(self):
        pass

    def findNextFromQueue(self):
        # print("Search for next from queue", self.queue)
        if self.queue:
            for info in self.queue:
                if info["type"] == "child":
                    # print("info:", info)
                    if self.onQueueCheck(info):
                        return self.getChildByName(info['name'])
                if info["type"] == "link":
                    if self.onQueueCheck(info):
                        input = TaskDescription(prompt=self.prompt, id=info["id"], stepped=True, parent=self, enabled= not self.is_freeze)
                        info["method"](input)
                        return self.getLinkedByName(info['name'])
        return None
    
    def isQueueComplete(self):
        if len(self.queue) > 0:
            return False
        return True

    def getNextFromQueue(self):
        res = self.findNextFromQueue()
        print("Get next from",self.getName(),"queue:", res)
        if res:
            return res
        return self.getNextFromQueueRe()
        # if self.isQueueComplete():
        #     return self.getNextFromQueueRe()
        # return None
        
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
    
    def setParam(self, param):
        pass
    
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
    
    def findKeyParam(self, text: str):
        return text
    