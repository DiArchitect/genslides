from genslides.task.presentation import PresentationTask
from genslides.task.base import BaseTask
from genslides.task.base import TaskDescription
from genslides.task.richtext import RichTextTask
from genslides.task.request import RequestTask
from genslides.task.response import ResponseTask
from genslides.task.collect import CollectTask
from genslides.task.group import GroupTask
from genslides.task.readfile import ReadFileTask
from genslides.task.writetofile import WriteToFileTask
from genslides.task.websurf import WebSurfTask
from genslides.task.readpage import ReadPageTask
from genslides.task.largetextresponse import LargeTextResponseTask

from genslides.task.writedialtofile import WriteDialToFileTask
from genslides.task.readdial import ReadDialTask

from genslides.task.gettime import GetTimeTask

from genslides.task.iteration import IterationTask, IterationEndTask
from genslides.task.runscript import RunScriptTask
from genslides.task.websurfarray import WebSurfArrayTask
from genslides.task.writejsontofile import WriteJsonToFileTask

from genslides.task.largedialresponse import LargeDialResponseTask

from genslides.task.setoptions import SetOptionsTask
from genslides.task.writetofileparam import WriteToFileParamTask
from genslides.task.readfileparam import ReadFileParamTask

from genslides.task.extproject import ExtProjectTask

import genslides.commands.create as cr

def checkTypeFromName(name : str, type :str) -> bool:
    stype = ''.join([i for i in name if not i.isdigit()])
    return stype.endswith(type)

def createTaskByType(type : str,info : TaskDescription):
    print('Create task')
    # if type == "Presentation":
        # return PresentationTask(info)
    stype = ''.join([i for i in type if not i.isdigit()])
    info.type = stype
    info.filename = type
    if stype.endswith("Text"):
        info.method = RichTextTask
        return cr.CreateCommand(info)
    if stype.endswith("Request"):
        info.method = RequestTask
        return cr.CreateCommand(info)
    if stype.endswith("LargeTextResponse"):
        info.method = LargeTextResponseTask
        return cr.CreateCommand(info)
    if stype.endswith("LargeDialResponseTask"):
        info.method = LargeDialResponseTask
        return cr.CreateCommand(info)
    if stype.endswith("Response"):
        info.method = ResponseTask
        return cr.CreateCommand(info)
    if stype.endswith("Group"):
        info.method = GroupTask
        return cr.CreateCommand(info)
    if stype.endswith("Collect"):
        info.method = CollectTask
        return cr.CreateCommand(info)
    if stype.endswith("ReadFile"):
        info.method = ReadFileTask
        return cr.CreateCommand(info)
    if stype.endswith("WriteToFile"):
        info.method = WriteToFileTask
        return cr.CreateCommand(info)
    if stype.endswith("WebSurf"):
        info.method = WebSurfTask
        return cr.CreateCommand(info)
    if stype.endswith("GetTime"):
        info.method = GetTimeTask
        return cr.CreateCommand(info)
    if stype.endswith("ReadPage"):
        info.method = ReadPageTask
        return cr.CreateCommand(info)
    if stype.endswith("ReadDial"):
        info.method = ReadDialTask
        return cr.CreateCommand(info)
    if stype.endswith("WriteDialToFile"):
        info.method = WriteDialToFileTask
        return cr.CreateCommand(info)
    if stype.endswith("Iteration"):
        info.method = IterationTask
        return cr.CreateCommand(info)
    if stype.endswith("IterationEnd"):
        info.method = IterationEndTask
        return cr.CreateCommand(info)
    if stype.endswith("RunScript"):
        info.method = RunScriptTask
        return cr.CreateCommand(info)
    if stype.endswith("WebSurfArray"):
        info.method = WebSurfArrayTask
        return cr.CreateCommand(info)
    if stype.endswith("WriteJsonToFile"):
        info.method = WriteJsonToFileTask
        return cr.CreateCommand(info)
    if stype.endswith("SetOptions"):
        info.method = SetOptionsTask
        return cr.CreateCommand(info)
    if stype.endswith("WriteToFileParam"):
        info.method = WriteToFileParamTask
        return cr.CreateCommand(info)
    if stype.endswith("ReadFileParam"):
        info.method = ReadFileParamTask
        return cr.CreateCommand(info)
    if stype.endswith("ExtProject"):
        info.method = ExtProjectTask
        return cr.CreateCommand(info)
    else:
    	return None
    
def getTasksDict() -> list:
    out = []
    out.append({"type":"Request","short":"Rq","creation":RequestTask})
    out.append({"type":"Response","short":"Rs","creation":ResponseTask})
    out.append({"type":"Collect","short":"Cl","creation":CollectTask})
    out.append({"type":"ReadDial","short":"Rd","creation":ReadDialTask})
    out.append({"type":"WriteDialToFile","short":"Wd","creation":WriteDialToFileTask})
    out.append({"type":"ReadFile","short":"Rf","creation":ReadFileTask})
    out.append({"type":"WriteToFile","short":"Wf","creation":WriteToFileTask})
    out.append({"type":"WriteToFileParam","short":"Wp","creation":WriteToFileParamTask})
    out.append({"type":"ReadFileParam","short":"Rp","creation":ReadFileParamTask})
    out.append({"type":"WriteJsonToFile","short":"Wj","creation":WriteJsonToFileTask})
    out.append({"type":"SetOptions","short":"So","creation":SetOptionsTask})
    out.append({"type":"RunScript","short":"Rs","creation":RunScriptTask})
    out.append({"type":"ExtProject","short":"Ep","creation":ExtProjectTask})
    return out
