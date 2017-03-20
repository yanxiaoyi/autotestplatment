# -*- coding:utf-8 -*-
#这里是核心控制器（脊椎）
from flask import render_template
from flask import request
from app import app
import json                  # Python build-in function
from flask import jsonify    # Flask build-in function
from case.public.public_method import AutoTestPlatForm
Atp=AutoTestPlatForm()    #平台系统，脚本库的功能



from flask import sessions
#服务器初始化自动加载
def toBeString(str):
    return str.decode("utf-8")

def getServerName(args):
    return Atp.getServerNames(args)

def interFaceList(mydata):
    return Atp.getinterFaceList(mydata)
def getInterFace():
    return Atp.getInterFace()
def getVersion(interface):
    return Atp.getVersion(interface)

#这里是交互
@app.route('/checkInterfaceName',methods=['GET', 'POST'])
def checkInterfaceName():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.checkInterfaceName(args)
@app.route('/getAllScripts',methods=['GET', 'POST'])
def getAllScripts():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.getAllScripts(args)

@app.route('/runScripts',methods=['GET', 'POST'])
def runScripts():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.runScripts(args)

@app.route('/runScript',methods=['GET', 'POST'])
def runScript():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    try:
        return Atp.runScript(args)
    except Exception as e:
        return jsonify(result={"msg":str(e)})


@app.route('/addInterface',methods=['GET', 'POST'])
def addInterface():
     if request.method == "POST":
        args = json.loads(request.data)["mykey"]
     else:
        args = json.loads(request.args.get('mykey'))
     return Atp.addInterface(args)

@app.route('/addScript',methods=['GET', 'POST'])
def addScript():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.addScript(args)

@app.route('/deleteScript',methods=['GET', 'POST'])
def deleteScript():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.deleteScript(args)

@app.route('/editScript',methods=['GET', 'POST'])
def editScript():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.editscript(args)


@app.route('/getVersion')
def returnVersion():
    print json.loads(request.args.get('mykey'))
    mydata = json.loads(request.args.get('mykey'))
    versionList=getVersion(mydata["msg"]);
    return jsonify(result=versionList);

@app.route('/getInterFaceList',methods=['GET', 'POST'])
def getinterFaceList():
       if request.method=="POST":
            args=json.loads(request.data)["mykey"]
       else:
            args=json.loads(request.args.get('mykey'))
       fff = interFaceList(args)
       return fff

@app.route('/addServerName',methods=['GET', 'POST'])
def addServerName():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.addServerName(args);

@app.route('/querySererName',methods=['GET', 'POST'])
def querySererName():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.queryServerName(args);


@app.route('/getServerName',methods=['GET', 'POST'])
def getServerNameForRe():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return jsonify(result={"serverNames":getServerName(args)});

@app.route('/checkScriptName',methods=['GET', 'POST'])
def checkScriptName():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.checkScriptName(args);

@app.route('/getServiceGroupList',methods=['GET', 'POST'])
def getServiceGroupList():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return Atp.getServiceGroupList(args);

@app.route('/queryServiceGroup',methods=['GET', 'POST'])
def queryServiceGroup():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return  Atp.queryServiceGroup(args);

@app.route('/addServiceGroup',methods=['GET', 'POST'])
def addServiceGroup():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return  Atp.addServiceGroup(args);

@app.route('/addServiceForServiceGroup',methods=['GET', 'POST'])
def addServiceForServiceGroup():
    if request.method == "POST":
        args = json.loads(request.data)["mykey"]
    else:
        args = json.loads(request.args.get('mykey'))
    return  Atp.addServiceForServiceGroup(args);

@app.route('/getProductList',methods=['GET', 'POST'])
def getProductList():
    return Atp.getProductList()


#日志模块
@app.route('/log_getFinalData',methods=['GET', 'POST'])
def getFinalData():
    return Atp.getFinalData()


@app.route('/')
@app.route('/index')
#页面实例化：加载所有用到的数据

def initialize():
    #user=User.getUser({"ip":request.remote_addr})
    #print "用户登录了 ",user["userName"]

    #print "这里监听相应",request.remote_addr
    #print log_main.product_serviceGroupList
    #fff=log_main.PlanningAndClassificationFordata();
    return render_template("/test.html",
                           title='Home',
                          )
