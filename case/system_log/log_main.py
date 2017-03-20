# -*- coding: UTF-8 -*-
from app.sql import querySQL
from flask import jsonify
from case.public.Text import TextView
import time
class Log_main:
    def __init__(self):
        try:#数据库连接
            self.con=querySQL.MYSQL('10.100.156.202', '*****', '*****',
                                       '*****', 3500)
            # 项目和组之间的关系
            self.project_serviceGroupList=self.getData({
                 "sql":"SELECT projectName,serviceGroup from project_servicegroup_manager",
                 "fathername": "projectName",
                 "sonlist": "ServiceGroup"
             })
            self.final_data=self.PlanningAndClassificationFordata()
            TextView.success("日志模块加载完成...")
        except Exception,e:
            TextView.error("日志模块加载失败...")

    #根据层级获取父级和子级的数据   
    def getData(self,hash):
        res = self.con.query(hash["sql"])
        project_serviceGroupList = {}    #返回值目录
        for project in res:
            list = []
            if (project[1] == "" or project[1] == None):
                project_serviceGroupList[project[0]] = {hash["sonlist"]: []}
                continue
            for serivceGroup in project[1].split(";"):
                if (serivceGroup == "" or serivceGroup == None): continue
                list.append(serivceGroup)
                project_serviceGroupList[project[0]] = {hash["sonlist"]: list}
        #print "这里存储第一层级",project_serviceGroupList
        return project_serviceGroupList

    #从项目-服务组-服务-接口-脚本
    def PlanningAndClassificationFordata(self):
        project_serviceGroupList=self.project_serviceGroupList
        pcData = {}
        projectAll=0
        ServiceGroupAll = 0
        ServiceAll = 0
        InterFaceAll = 0
        ScriptsAll = 0
        for project in project_serviceGroupList:
            if "调试测试用".decode('utf-8') == project: continue
            projectAll+=1
            for ServiceGroup in project_serviceGroupList[project]["ServiceGroup"]:
                ServiceGroupAll+=1
                sql = "SELECT GroupName,serverNames from servicegroup_server_manager where GroupName='%s'" % (
                ServiceGroup)
                res = self.getData({
                    "sql": sql,
                    "fathername": "ServiceGroup",
                    "sonlist": "Service"
                })
                for Service in res[ServiceGroup]["Service"]:
                    ServiceAll += 1
                    sql = "SELECT serverName,interfaceName from server_interface_manager where serverName='%s'" % (
                    Service)
                    res2 = self.getData({
                        "sql": sql,
                        "fathername": "Service",
                        "sonlist": "Interface"
                    })
                    if res2.has_key(Service):
                        if res2[Service].has_key("Interface"):
                            #print "这里是服务接口", project, "------", ServiceGroup, "-----", Service, "-----", res2[Service][
                            #    "Interface"].__len__(), res2[Service]["Interface"]
                            for Interface in res2[Service]["Interface"]:
                                InterFaceAll += 1
                                name = Service + "_".decode('utf-8') + Interface + "_scripts".decode('utf-8')
                                sql = "SELECT count(*) from `%s`" % (name)
                                res = self.con.query(sql)
                                #print Interface, "下有", res[0][0], "个脚本"
                                ScriptsAll += res[0][0]
                        else:
                            pass
                            #print "服务", Service, "没有子接口"
                    else:
                        pass
                        
        pcData["ScriptsAll"]=ScriptsAll
        pcData["InterFaceAll"]=InterFaceAll
        pcData["ServiceAll"]=ServiceAll
        pcData["ServiceGroupAll"]=ServiceGroupAll
        pcData["projectAll"]=projectAll
        pcData["time"]= time.strftime('%Y-%m-%d %X', time.localtime())
        return pcData

    #这里是日志系统的汇总反馈
    def getFinalData(self):
        return jsonify(result={"final_data":self.final_data})



