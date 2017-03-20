# -*- coding:utf-8 -*-
from app.sql import querySQL
import json
from flask import jsonify
from case.travelgroupservice.travelgroupservice_public import service as travelgroupservice_server
from Expected_Result import Expected_Result
import traceback
import re
import time
from case.public.UserInfo import UserInfo
from case.system_log.log_main import Log_main

def String(self):
       return self.decode("utf-8")
scriptsInfoList = []
User = UserInfo()        #用户系统
ER=Expected_Result()   #期望值系统
log_main=Log_main()    #日志模块系统


class AutoTestPlatForm:
    def __init__(self):
        #self.con = querySQL.MYSQL('10.101.50.21', 'admin', '123456', 'interface_test', 3500)
        self.con = querySQL.MYSQL('10.100.156.202', '*********', 'aqTNWX0l3RlrUIcTMciVR1Ef','*******', 3500)

    #二级模块-------脚本库
    # 获取服务列表名称
    def getServerNames(self,mydata):
        serviceGroupName=mydata["ServiceGroupName"]
        sql="SELECT serverNames from servicegroup_server_manager where GroupName='%s'"%(serviceGroupName)
        serverList = self.con.query(sql)
        print serverList
        if(serverList==()):
            return []
        if(serverList[0][0]==None):
            return []
        sql = 'SELECT serverName,service_detail from server_interface_manager '
        result = self.con.query(sql)
        #print "这里是服务组里面的服务",serverList
        #print "这里是服务",result
        serverName = []
        for service in result:
            if service[0] in serverList[0][0].split(";"):
                #print "这里是service",service,service[0],service[1]
                if (service[1] == None):
                    detail = ""
                else:
                    detail = service[1]
                if {"Name": service[0],"Detail":detail} not in serverName:
                    serverName.append({"Name": service[0],"Detail":detail})

        #print "返回的情况",serverName
        return sorted(serverName, key=lambda serverName: serverName["Name"].lower())

    #查询脚本名称
    def queryServerName(self,mydata):
        #print "这里是传递过来的参数",mydata
        serviceGroup=mydata["serviceGroup"]
        ServiceName= mydata["ServiceName"]
        sql = "SELECT serverNames from servicegroup_server_manager where GroupName='%s'" % (serviceGroup)
        serverList = self.con.query(sql)
        #print "这是总的",serverList
        if (serverList == ()):
            return jsonify(result={"Exist": False})
        if (serverList[0][0] == None):
            return jsonify(result={"Exist": False})
        if ServiceName in serverList[0][0].split(";"):
            return jsonify(result={"Exist": True})
        else:
            return jsonify(result={"Exist": False})

    # 获取所有接口名称
    def getinterFaceList(self,mydata):
        serverName=mydata["msg"]
        sql="SELECT interfaceName  from server_interface_manager where servername='%s' " %(serverName)
        result = self.con.query(sql)
        list=[]
        if result[0][0] is None:
            return jsonify(result={"ServerName":mydata["msg"],"InterFaceName":"None"})
        #print result[0][0],"getinterFaceList 的结果"
        for iFN in result[0][0].split(";"):
            if(iFN==""):continue;
            detail=self.getInterFaceDetail({"InterFaceName":iFN,"ServiceName":serverName})
            list.append({"Name":iFN,"detail":detail})

        list = sorted(list, key=lambda interFace: interFace["Name"].lower())
       # print list,"dsdsdsdsdsdsd"
        return jsonify(result={"ServerName":mydata["msg"],"InterFaceName":list})

    def getInterFaceDetail(self,mydata):
        interfaceName = mydata["InterFaceName"]
        ServiceName = mydata["ServiceName"]
        sql="SELECT detail from server_interface_detail_manager where interfaceName='%s' and serviceName='%s'"%(interfaceName,ServiceName)
        result = self.con.query(sql)
        #print result,"1213131111111111111111111"
        if(result==()):
            detail = ""
        elif(result[0][0]==None):
            detail=""
        else:
            detail=result[0][0]
        return detail


    def getInterFace(self):
        sql = 'SELECT interface  from interface_testcase_manager '
        result = self.con.query(sql)
        print result
        interFace = []
        for interface in result:
            if {"Name": interface[0]} not in interFace:
                interFace.append({"Name": interface[0]})
        return sorted(interFace, key=lambda interFace: interFace["Name"].lower())
        #return interFace

    # 获取接口所对应的版本号
    def getVersion(self,interface):
        print interface
        sql = 'SELECT version  from interface_testcase_manager where interface="%s"' % (interface)
        result = self.con.query(sql)
        print result
        versionList = []
        for version in result:
            versionList.append({"version": version[0]})
        return versionList

    
    def getAllScripts(self,mydata):
        global scriptsInfoList
        serverName=mydata["serverName"]
        interface = mydata["interfaceName"]
        if ((serverName + "_" + interface + "_scripts").__len__() > 64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interface[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interface + "_scripts"
        sql = "select * from `%s`" % (SimplifiedName)
        scriptsInfo = self.con.query(sql)
        info = []
        for index, script in enumerate(scriptsInfo):
            info.append({"serverName":serverName,"name": script[0], "arguments": script[2], "method": script[3], "effective_condition": script[4],
                         "desc": script[5], "result": script[0], "interface_version": serverName+":"+interface + ":" + script[8],
                         "url":script[6],"methodName":script[7],"version":script[8] })
        scriptsInfoList.extend(info)
        return jsonify(result=info)

    def checkString(self,str):  
        replace_reg = re.compile(r':True,')
        str = replace_reg.sub(':"True",', str)
        replace_reg = re.compile(r':False,')
        str = replace_reg.sub(':"False",', str)
        return str
    #单条脚本
    def runScript(self,mydata,runAll=False):
        non_jsonFlag=False
        #print "runScript里面的检查!!!!"
        #print mydata["arguments"]
        if ("True" in mydata["arguments"]) or ("False" in mydata["arguments"]):
            mydata["arguments"]=self.checkString(mydata["arguments"])
        params = mydata["arguments"]
        effective_condition = mydata["effective_condition"]
        try:
            params = json.loads(mydata["arguments"])
        except Exception,e:
            print "trans params failed..."
            print str(e), traceback.print_exc()
        try:
            effective_condition = json.loads(mydata["effective_condition"])
        except Exception ,e:
            print "trans expect failed..."
            print str(e),traceback.print_exc()
        flag=False
        if (mydata["method"]==None or mydata["method"]==""):
            flag=False
        elif (mydata["method"].lower()=="get"):
            flag=True
        if(flag):
            fff = travelgroupservice_server(mydata['methodName'], mydata['url']).Except_get(
                params=params
            )
        else:
            fff = travelgroupservice_server(mydata['methodName'],mydata['url']).Except_post(
                params=params
             )
        mmm=None
        jsonFlag=False
        ResultFromServer={"other":fff["result"]["other"]}
        try: #这里是期望效果      
            ResultFromServer["content"] = json.loads(fff["result"]["content"])
            jsonFlag=True
        except Exception,e:
            try:                   
                ResultFromServer["content"]=self.reg_json(fff["result"]["content"])
                jsonFlag = True
            except Exception,e:
                try:              
                    if str(fff["result"]["content"]).lower()=='true' or str(fff["result"]["content"]).lower()=='false':
                        ResultFromServer["content"]=fff["result"]["content"]
                        non_jsonFlag=True
                    elif fff["result"]["content"]=="":
                        ResultFromServer["content"] = fff["result"]["content"]
                        non_jsonFlag = True
                    else:
                        raise "error: response coulde not resolution"
                except Exception,e:
                    print "Return_result_transformation_Error";str(e);traceback.print_exc()

        if jsonFlag or non_jsonFlag:
            try:
                mmm = ER.Expecte_expected_results(effective_condition, ResultFromServer)
                #print "这里是检测的返回值",mmm
            except Exception,e:
                print "Expect_result_Error";str(e);traceback.print_exc()
        if not mmm:
            if jsonFlag:
                mmm={"msg":"期望信息结果异常...","result":"error"}
            else:
                mmm = {"msg": "返回结果转化异常...", "result": "error"}
        #print "这里是最终返回值",fff["result"]["content"],type(fff["result"]["content"])
        if runAll:
            return {"msg": fff["msg"], "result": fff["result"]["content"], "marry": mmm}
        else:
            return jsonify(result={"result": fff["result"]["content"], "marry": mmm})

    #reg_json  纠正json序列化格式错误
    def reg_json(self,ResultFromServer):
        #print "传进来要被矫正的值"
        #print ResultFromServer
        ResultFromServer = ResultFromServer.replace("\\r", "\\\\r").replace("\\n", "\\\\n")
        int_values = re.findall(r"\"(.*?)\"\:(.*?)\,", ResultFromServer)
        for i in int_values:
            if "\"" in i[1]:  # 这里后续替换成正则
                continue  # 正常的字符
            else:
                if (re.match(r"\d+$", i[1]) and True or False):
                    continue  # 是数字
                else:
                    #print str(i[1]) + "   将被转换"
                    # ResultFromServer = ResultFromServer.replace("\"" + i[0] + "\":" + i[1] + ",","\"" + i[0] + "\":\"" + i[1] + "\",")
                    ResultFromServer = re.sub(r'\"%s\"\:%s\,' % (i[0], i[1]), "\"" + i[0] + "\":\"" + i[1] + "\",",
                                              ResultFromServer)
        #print "被修正之后的"
        #print ResultFromServer
        ResultFromServer=json.loads(ResultFromServer)
        return ResultFromServer

    #运行被选中的脚本
    def runScripts(self,mydata):
        start=time.clock()
        result_All = {}
        for key in mydata:
            result_mydata_key = {}
            for my in mydata[key]:
                fff=self.runScript(my,runAll=True)
                result = {}
                if fff["msg"] == "error":
                    result = {"name": my["name"], "msg": "error", "detail": fff["result"],"marry":fff["marry"]}
                else:
                    result = {"name": my["name"], "msg": "Success", "interface_version": my["interface_version"],"detail": fff["result"],"marry":fff["marry"]}
                result_mydata_key[result["name"]] = result
            result_All[key] = result_mydata_key
        end = time.clock()
        result_All["runtime"]=end-start
        return jsonify(result=result_All)

    # 增加服务
    def addServerName(self,mydata):
        fff = travelgroupservice_server("1111", "2222").addServerName(mydata)
        print "这里是返回结果",fff
        if fff ==():
            return jsonify(result={"Success": "ok"})
        else:
            return jsonify(result={"Success": "failed", "msg": fff})
    #增加接口
    def addInterface(self,mydata):
        try:
            fff = travelgroupservice_server("1111","2222").addInterface(mydata)
            if fff==():
                return jsonify(result={"Success": "ok"})
            else:
                return jsonify(result={"Success": "failed","msg":fff["msg"]})
        except Exception ,e:
            return jsonify(result={"Success": "failed","msg":"异常："+str(e)})

    #增加脚本
    def addScript(self,mydata):

        try:
            fff = travelgroupservice_server("1111","2222").addScript(mydata)
        except Exception,e:
            print str(e),fff
            return jsonify(result={"Success": "failed"})
        if fff==():
            return jsonify(result={"Success": "ok"})
        else:
            return jsonify(result={"Success": "failed"})

    #删除脚本
    def deleteScript(self,mydata):
        fff = travelgroupservice_server("1111","2222").deletescript(mydata)
        return jsonify(result={"Success": fff})
    #编辑脚本
    def editscript(self,mydata):
        try:
             fff = travelgroupservice_server("1111","2222").editscript(mydata)
        except Exception, e:
             print str(e),fff
             return jsonify(result={"Success": "failed"})
        if fff==():
            return jsonify(result={"Success": "ok"})
        else:
            return jsonify(result={"Success": "failed"})

    #查询接口
    def checkInterfaceName(self,mydata):
        #print mydata
        serverName=mydata["serverName"]
        interfaceName=mydata["interface"]
        fff = travelgroupservice_server("1111", "2222").queryInterface(serverName)
        if fff is None:
            return jsonify(result={"Exist": "yes"})
        if interfaceName not in fff.split(";"):
            return  jsonify(result={"Exist": "yes"})
        else:
            return jsonify(result={"Exist": "no"})

    def checkScriptName(self,mydata):
        print mydata
        serverName = mydata["serverName"]
        interfaceName = mydata["interfaceName"]
        scriptName=mydata["scriptName"]
        fff=travelgroupservice_server("1111", "2222").queryScript(serverName,interfaceName)
        print fff
        if scriptName not in fff:
            return jsonify(result={"Success": "yes"})
        else:
            return jsonify(result={"Success": "no"})

    #获取服务组列表
    def getServiceGroupList(self,mydata):
        fff = travelgroupservice_server("1111", "2222").getServiceGroupList(mydata)
        return jsonify(result={"list": fff})

    def queryServiceGroup(self,mydata):
        fff=travelgroupservice_server("1111", "2222").queryServiceGroup(mydata)
        return jsonify(result={"Exist": fff})

    def addServiceGroup(self,mydata):
        fff = travelgroupservice_server("1111", "2222").addServiceGroup(mydata)
        return jsonify(result={"Success": fff})

    def addServiceForServiceGroup(self,mydata):
        fff = travelgroupservice_server("1111", "2222").addServiceForServiceGroup(mydata)
        return jsonify(result={"Success": fff})

    def getProductList(self):
        fff = travelgroupservice_server("1111", "2222").getProductList()
        return jsonify(result={"ProductList": fff})



    #二级模块-----日志模块
    def getFinalData(self):
        return log_main.getFinalData()
