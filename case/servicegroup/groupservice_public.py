# -*- coding:utf-8 -*-
from case.public import http
from app.sql import querySQL
import time
import re


ISOTIMEFORMAT='%Y-%m-%d %X'
class service():
    def __init__(self, api_name,url):
        self.api_name = api_name
        # self.port = 'http://10.100.159.58:8000/dsf/iv/product/baseproductmodify'
        if "http" in url:
            self.url=url
        else:
            self.url="http://"+url
        #self.con=querySQL.MYSQL('10.101.50.21', 'admin', '123456', 'interface_test', 3500)
        self.con = querySQL.MYSQL('10.100.156.202', '****', '*****',
                                  '*****', 3500)
    def post(self,params,flag):
        #print "这里是被传递的参数",type(params),params
        try:
            if("(" in self.api_name) and (")" in self.api_name):
                interface = re.findall(r"(.*)\([^()]*\)", self.api_name)[0]
            else:
                interface=self.api_name
            if(flag=="post"):
                httpPost = http.Http(
                    url=self.url,
                    timeout=10,
                    hash=params,
                    interface=interface).post()
            else:
                httpPost = http.Http(
                    url=self.url,
                    timeout=10,
                    hash=params,
                    interface=interface).get()
            print httpPost
            return {"msg":"Success","result":httpPost}
        except Exception as e:
            return {"msg":"error","result":str(e)}



    def Except_post(self, params):
        return self.post(params,"post")
    def Except_get(self, params):
        return self.post(params,"get")

    def deletescript(self,mydata):
        interfaceName = mydata["methodName"]
        serverName = mydata["serverName"]
        name = mydata["name"]
        if ((serverName + "_" + interfaceName + "_scripts").__len__() > 64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interfaceName[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interfaceName + "_scripts"
        sql="DELETE from `%s` where name='%s'" %(SimplifiedName, name)
        res=self.con.query(sql)
        if res==():
            return True
        else:
            return False

    def getSciptName(self,interface,version):
        # 获取用例名
        sql = 'SELECT casename  from interface_testcase_manager where interface="%s" and version="%s"' % (
            interface, version)
        casename = self.con.query(sql)[0][0]

        # 获取脚本名
        sql = 'SELECT scriptnames  from testcase_scripts_manager where casename="%s"' % (casename)
        scriptnames = self.con.query(sql)[0][0]

        return scriptnames
    def getCount(self,casename):
        sql="SELECT count(*) from `%s`"%(casename)
        res = self.con.query(sql)
        return res[0][0]

    def addScript(self,newScript):
        serverName = newScript["serverName"]
        interfaceName = newScript["interfaceName"]
        name = newScript["name"]
        arguments = newScript["arguments"]
        method = newScript["method"]
        description = newScript["detail"]
        url=newScript["url"]
        version=newScript["version"]
        effective_condition=newScript["except_effect"]

        if ((serverName + "_" + interfaceName + "_scripts").__len__() > 64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interfaceName[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interfaceName + "_scripts"
        
        if  "'"in effective_condition : effective_condition=effective_condition.replace("'","''")
        sql="INSERT INTO `%s` (`name`,`arguments`, `method`, `expect`, `description`,`url`,`methodName`,`version`) VALUES ('%s','%s', '%s', '%s', '%s','%s','%s','%s');"%(SimplifiedName,name,arguments,method,effective_condition,description,url,interfaceName,version)
        #print sql
        res = self.con.query(sql)
        return res

   	   def addInterface(self,newInterface):
        #print newInterface
        interfaceName=newInterface["interface"]
        serverName=newInterface["serverName"]
        inserttime = time.strftime(ISOTIMEFORMAT, time.localtime())
        queryResult=self.queryInterface(serverName)
        #print "这是查询",queryResult
        if queryResult is None or queryResult=="":
            result=interfaceName
        else:
            InterFaceList=self.queryInterface(serverName).split(";")
            if interfaceName in InterFaceList:
                return {"msg":"数据库中已存在相同的接口名称"}
            result=self.queryInterface(serverName)+";"+interfaceName

        if((serverName + "_" + interfaceName + "_scripts").__len__()>64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interfaceName[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interfaceName + "_scripts"
        
        sql = '''CREATE TABLE `%s` (name VARCHAR(100) NULL,id INT NOT NULL AUTO_INCREMENT,arguments VARCHAR(3000) NULL,method VARCHAR(100) NULL,expect VARCHAR(3000) NULL,description VARCHAR(100) NULL,url VARCHAR(200) NULL,methodName VARCHAR(200) NULL,version VARCHAR(30) NULL,PRIMARY KEY (id))''' % (
            SimplifiedName
        )
        res = self.con.query(sql)
        
        sql = "UPDATE server_interface_manager SET interfaceName = '%s',`updataTime` ='%s'  WHERE serverName = '%s'" % (result,inserttime,serverName)
        self.con.query(sql)
        self.add_interface_detail(newInterface)  
        
        return res

    def add_interface_detail(self,newInterface):
        interfaceName = newInterface["interface"]
        serverName = newInterface["serverName"]
        InterFaceDetail = newInterface["detail"]
        newtime = time.strftime(ISOTIMEFORMAT, time.localtime())
        sql="INSERT INTO `server_interface_detail_manager` (`interfaceName`, `serviceName`, `detail`,`updateTime`) VALUES ('%s', '%s','%s','%s')"%(interfaceName,serverName,InterFaceDetail,newtime)
        self.con.query(sql)


    def editscript(self, newScript):
        #print newScript
        serverName=newScript["serverName"]
        interfaceName = newScript["interfaceName"]
        name = newScript["name"]
        argument = newScript["arguments"]
        method = newScript["method"]
        description = newScript["detail"]
        url= newScript["url"]
        version = newScript["version"]
        effective_condition = newScript["except_effect"]
        methodName=interfaceName
        if ((serverName + "_" + interfaceName + "_scripts").__len__() > 64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interfaceName[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interfaceName + "_scripts"
        if "'" in effective_condition: effective_condition = effective_condition.replace("'", "''")
        sql = "UPDATE `%s` SET arguments = '%s', method = '%s', expect = '%s', description = '%s', url='%s' , methodName='%s',version='%s' WHERE name = '%s'" % (
            SimplifiedName, argument, method, effective_condition, description, url, methodName,version, name)
        
        res = self.con.query(sql)
        return res

    def addServerName(self,mydata):
        self.addServiceForServiceGroup(mydata)
        ServiceName=mydata["ServiceName"]
        ServiceDetail=mydata["ServiceDetail"]
        sql="select id from server_interface_manager where serverName='%s'"%(ServiceName)
        res = self.con.query(sql)
        if res==():
            newtime = time.strftime(ISOTIMEFORMAT, time.localtime())
            sql = "INSERT INTO server_interface_manager (`serverName`, `updataTime` ,`service_detail`) VALUES ('%s', '%s', '%s')" % (ServiceName,newtime,ServiceDetail)
            res = self.con.query(sql)
            return res
        else:
            return "ServiceName already Exist"

    def queryInterface(self,name):
        sql='SELECT interfaceName from server_interface_manager where serverName="%s"'%(name)
        res=self.con.query(sql)
        
        return res[0][0]

    def queryScript(self,serverName,interfaceName):
        if ((serverName + "_" + interfaceName + "_scripts").__len__() > 64):
            num = 64 - serverName.__len__() - "_scripts".__len__() - 1
            SimplifiedName = serverName + "_" + interfaceName[0:num] + "_scripts"
        else:
            SimplifiedName = serverName + "_" + interfaceName + "_scripts"
        sql = 'SELECT name from `%s`  '% (SimplifiedName)
        #print sql
        res = self.con.query(sql)
        list=[]
        for re in res:
            for r in re:
                list.append(r)
        return list

    #获取服务组列表
    def getServiceGroupList(self,mydata):
        serviceGroupNameList=mydata["serviceGroupNameList"]
        
        list = []
        for serviceGroupName in serviceGroupNameList:
            sql = "SELECT GroupName,detail from servicegroup_server_manager where GroupName='%s'" % (serviceGroupName)
            res = self.con.query(sql)
            for serviceGroup in res:
                if (serviceGroup[1] == None):
                    detail = ""
                else:
                    detail = serviceGroup[1]
            list.append({"ServiceGroup": serviceGroup[0], "detail": detail})
        
        return list

    def queryServiceGroup(self,mydata):
        productName=mydata["ProductName"]
        serviceGroupName=mydata["ServiceGroupName"]
        
        sql = "SELECT serviceGroup from product_servicegroup_manager where productName = '%s'" % (productName)
        res = self.con.query(sql)
        if (res[0][0] is None or res[0][0]==""):
            pass
        else:
            list = res[0][0].split(";")
            list.pop()
            if serviceGroupName in list:
                return False
        sql="SELECT GroupName from servicegroup_server_manager where GroupName='%s'"%(serviceGroupName)
        res = self.con.query(sql)
        if res == ():
            return True
        if res[0][0]==serviceGroupName:
            return False
        else:
            return True

    def addServiceGroup(self,mydata):
        
        productName = mydata["ProductName"]
        serviceGroupName = mydata["ServiceGroupName"]
        sql = "SELECT serviceGroup from product_servicegroup_manager where productName = '%s'" % (productName)
        res = self.con.query(sql)
        serviceGroupNameList=res[0][0]
        if(res[0][0]==None or res[0][0]==""):
            serviceGroupNameList=serviceGroupName+";"
        else:
            serviceGroupNameList += serviceGroupName+";"
        sql = "UPDATE `product_servicegroup_manager` SET serviceGroup = '%s' WHERE productName = '%s'"%(serviceGroupNameList,productName)
        res = self.con.query(sql)
        
        detail=mydata["detail"]
        newtime = time.strftime(ISOTIMEFORMAT, time.localtime())
        sql="INSERT INTO `servicegroup_server_manager`(`GroupName`,`updateTime`,`detail`) VALUES ('%s','%s','%s')" %(serviceGroupName,newtime,detail)
        res = self.con.query(sql)
        return True

    def addServiceForServiceGroup(self,mydata):
        serviceGroup=mydata["serviceGroup"]
        ServiceName=mydata["ServiceName"]
        sql="SELECT serverNames from servicegroup_server_manager where GroupName='%s'"%(serviceGroup)
        serverList = self.con.query(sql)
        
        newServerList=""
        if (serverList == ()):
            newServerList=ServiceName+";"
        elif(serverList[0][0] == None):
            newServerList=ServiceName+";"
        else:
            
            newServerList=serverList[0][0]+ServiceName+";".decode('utf-8')
            
        sql = "UPDATE `servicegroup_server_manager` SET serverNames = '%s' WHERE GroupName = '%s'" % (newServerList,serviceGroup)
        res = self.con.query(sql)
        if res==():
            return True
        else:
            return False

    def getProductList(self):
        sql = "SELECT * from product_servicegroup_manager"
        res = self.con.query(sql)
        #print res
        list=[]
        for product in res:
             ServiceGroupList=[]
             #print product[2],product[2] is None,product[2] == None
             if(product[2] is None or product[2]==""):
                 pass
             else:
                 for ServiceGroupName in product[2].split(";"):
                     if (ServiceGroupName=="")or(ServiceGroupName==None):continue;
                     ServiceGroupList.append(ServiceGroupName)
             list.append({"Name":product[1],"ServiceGroupList":ServiceGroupList})
        
        return list
