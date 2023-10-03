from genslides.task.base import TaskManager
from genslides.utils.savedata import SaveData
from genslides.utils.archivator import Archivator
from genslides.commanager.jun import Manager

from os import listdir
from os.path import isfile, join


import os
import json
import gradio as gr
import graphviz
import pprint
import py7zr
import datetime
import shutil


class Projecter:
    def __init__(self, manager : Manager = None) -> None:
        mypath = "projects/"
        self.ext_proj_names = []
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        self.mypath = mypath
        task_man = TaskManager()
        self.savedpath = task_man.getPath()
        self.manager = manager
        self.manager.loadTasksList()
        # saver = SaveData()
        # saver.removeFiles()
        self.current_project_name = self.manager.getParam("current_project_name")
        self.updateSessionName()


    def updateSessionName(self):
        self.session_name = self.current_project_name + "_" + datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        print("Name of session=",self.session_name)
        self.manager.setParam("session_name",self.session_name)


    def getTaskJsonStr(self, id : str):
        out = self.manager.getTaskJsonStr()
        out['id'] = id
        out['name'] = self.current_project_name
        return out

    def loadList(self):
        mypath = self.mypath
        onlyfiles = [f.split('.')[0] for f in listdir(mypath) if isfile(join(mypath, f))]
        return onlyfiles
    
    def clearFiles(self):
        mypath = self.savedpath
        for f in listdir(mypath):
            f_path = join(mypath, f)
            if isfile(f_path):
                os.remove(f_path)
            else:
                shutil.rmtree(f_path)

    def clear(self):
        self.clearFiles()
        self.manager.onStart() 

    def getEvaluetionResults(self, input):
        print("In:", input)
        saver = SaveData()
        saver.updateEstimation(input)




    def load(self, filename):
        if filename == "":
            return ""
        self.clearFiles()
        print(self.savedpath)
        Archivator.extractFiles(self.mypath, filename, self.savedpath)
        self.manager.onStart() 
        self.manager.loadTasksList()
        self.current_project_name = filename
        self.manager.setParam("current_project_name",self.current_project_name)
        self.updateSessionName()
        return filename
    
    def append(self, filename):
        if filename + '.7z' in [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]:
            ext_pr_name = 'pr' + str(len(self.ext_proj_names))
            trg = os.path.join(self.savedpath,'ext', ext_pr_name) +'/'
            Archivator.extractFiles(self.mypath, filename, trg)
            print('Append project',filename,'task to', trg)
            proj_file = 'proj.json'
            proj_path = os.path.join(self.savedpath, proj_file)
            if os.path.exists(proj_path):
                pass
            else:
                proj_obj = {"appended": [{"src":filename, "pt": ext_pr_name}]}
                with open(proj_path, 'w') as f:
                    json.dump(proj_obj,f,indent=1) 

            self.ext_proj_names.append(ext_pr_name)

            self.manager.appendExtendProjectTasks(trg, ext_pr_name)
            cur = self.manager.curr_task
            task_man = TaskManager()
            task_man.setDefaultProj()
            self.manager.makeTaskAction(ext_pr_name,"ExtProject","New","user")
            if cur != self.manager.curr_task and cur is not None:
                print('Successfully add external task')
            print('List of tasks:',[n.getName() for n in self.manager.task_list])

    
    def save(self, name):
        self.current_project_name = name
        self.manager.setParam("current_project_name",self.current_project_name)

        # Archivator.saveOnlyFiles(self.savedpath, self.mypath, name)
        Archivator.saveAll(self.savedpath, self.mypath, name)

        return gr.Dropdown.update( choices= self.loadList(), interactive=True)

