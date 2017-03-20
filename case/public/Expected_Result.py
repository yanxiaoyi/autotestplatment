# -*- coding:utf-8 -*-
import traceback
import json
import re
import time

#转码
def unicode_to_string(str2):
    if str(type(str2))=="<type 'dict'>" or str(type(str2))=="<type 'list'>"or str(type(str2))=="<type 'bool'>" or str(type(str2))=="<type 'int'>" :return str(str2)
    if str(type(str2))=="<type 'str'>":return str2
    return str2.encode('utf-8')
class Expected_Result():

    class switch(object):
        def __init__(self, value):
            self.value = value
            self.fall = False

        def __iter__(self):
            """Return the match method once, then stop"""
            yield self.match
            raise StopIteration

        def match(self, *args):
            """Indicate whether or not to enter a case suite"""
            if self.fall or not args:
                return True
            elif self.value in args:  # changed for v1.5, see below
                self.fall = True
                return True
            else:
                return False


    #做一个简单的类型递归
    def getType(self,object):
        if(str(type(object)))=="<type 'dict'>":
            return
        if(str(type(object)))=="<type 'list'>":
            return
        if (str(type(object))) == "<type 'int'>":
            return
        if (str(type(object))) == "<type 'str'>":
            return


    #期望效果的有效判定
    def Expecte_expected_results(self,effective_condition,ResultFromServer):
        result_all={}
        if str(type(effective_condition)) != "<type 'dict'>":
            #print "这里显示期望类型",effective_condition
            effective_condition=json.loads(effective_condition)
            #这里后续要补个保护
        #print type(effective_condition),effective_condition
        for ziduan in effective_condition:
            #print ziduan,"这里是字段名称key"
            result_all[ziduan]={}
            for tiaojian in effective_condition[ziduan]:
                #print ziduan,type(ziduan),tiaojian["type"],type(tiaojian["type"]), tiaojian["value"],type(tiaojian["value"]),"期望效果判定中"  #这里是字段-----选择的匹配类型--匹配结果
                try:
                    if(self.check_the_type(tiaojian["type"])=="response_other"):
                      
                       result_all[ziduan][tiaojian["type"]]=self.response_other(ziduan,tiaojian["type"],tiaojian["value"],ResultFromServer["other"])
                    else:
                        
                        result_all[ziduan][tiaojian["type"]]=getattr(self,self.check_the_type(tiaojian["type"]))(ziduan,tiaojian["type"],tiaojian["value"],ResultFromServer["content"])
                except Exception, e:
                    print "bug:", str(e);traceback.print_exc()
                    continue;
        return result_all
    #只负责返回方法名称
    def check_the_type(self,*args):
        vvv=args[0].encode('utf-8')
        for case in self.switch(vvv):
            if case('int-等值匹配'):return "int_equal_match"
            if case('int-期望值范围'):return "int_expected_range"
            if case('int-期望值长度'):return "int_expected_length"
            if case('int-期望值长度范围'):return "int_expected_length_range"
            if case('int-模糊查找'):return "int_fuzzy_search"
            if case('string-等值匹配'):return "string_equal_match"
            #if case('string-期望值范围'):return "string_expected_range"
            if case('string-期望值长度'):return "string_expected_length"
            if case('string-期望值长度范围'):return "int_expected_length_range"
            if case('string-模糊查找'):return "string_fuzzy_search"
            if case('date-等值匹配'):return "data_equal_match"
            if case('date-期望值范围'):return "data_expected_range"
            if case('date-模糊查找'):return "data_fuzzy_search"
            if case('bool-等值匹配'):return "bool_equal_match"
            if case('正则匹配'):return "reg_match"
            if case('[]-列表(数组)匹配'):return "list_match"
            if case('{}-字典(哈希)匹配'):return "dict_match"
            if case('response-其他属性'):return "response_other"
            #if case(): return "string_fuzzy_search"
            if case('非json格式验证'):return "non_json_format"


    #控制匹配的返回信息
    def getMsg(self,type2,field,require="",value="",value2=""):
        #print type(field),type(value),type(value2),"zzzzzzz"
        field=unicode_to_string(field)
        value=unicode_to_string(value)
        require=unicode_to_string(require)
        value2=unicode_to_string(value2)
        if type2=="success":
            if value !="":
                return ("字段：" + field +"  "+require+"有效"+"::模糊匹配到的字段为："+value).decode('utf-8')
            else:
                return ("字段：" + field + "  " + require + "有效").decode('utf-8')
        if type2=="failed" :return ("返回信息中存在字段："+ field + "，但值不匹配："+ value + " && " + value2).decode('utf-8')
        if type2=="error"  : return ("返回结果中未发现任何字段名为："+ field + "的字段").decode('utf-8')
        if type2=="fuzzy_error":return ("模糊查找未匹配到："+value).decode('utf-8')
        if type2=="fuzzy_success":return ("模糊查找匹配到:"+ value).decode('utf-8')
        if type2 == "expect_field_error":return ("期望字段匹配错误:"+ value).decode('utf-8')
    #由于目前业务的关系，数组并不适合拆分开来，一般里面都是参数相同的各种结果
    def getFiled(self,ResultFromServer):
        hhh={}
        #print "注入结果",ResultFromServer.__len__()
        if str(type(ResultFromServer))=="<type 'list'>":
            ResultFromServer=ResultFromServer[0]   #这里做了一个简单的匹配，后续大结构再补
        #print "注入结果",type(ResultFromServer),ResultFromServer
        for rf in ResultFromServer:
                #print "这是被比对的",str(type(ResultFromServer[rf]))
                if str(type(ResultFromServer[rf])) == "<type 'dict'>":
                       hhh[rf]=ResultFromServer[rf]
                       hhh.update(self.getFiled(ResultFromServer[rf]))
                elif str(type(ResultFromServer[rf])) == "<type 'str'>":
                       hhh[rf]=ResultFromServer[rf].encode('utf-8')
                else:
                       hhh[rf] = ResultFromServer[rf]
        #print hhh,"这是最终转换结果"
        return hhh
    #int_等值匹配
    def int_equal_match(self,field,require,value,ResultFromServer):
            ResultFromServer = self.getFiled(ResultFromServer)
            if ResultFromServer.has_key(field):
                if str(type(ResultFromServer[field]))=="<type 'unicode'>":
                    ResultFromServer[field] = unicode_to_string(ResultFromServer[field]);
                else:
                    ResultFromServer[field]=str(ResultFromServer[field])
                value = unicode_to_string(value);
                if ResultFromServer[field] == value:
                    msg =self.getMsg("success",field,require)
                    return {"msg": msg, "result": "success"}
                else:
                    msg =self.getMsg("failed",field,value=value,value2=ResultFromServer[field])
                    return {"msg": msg, "result": "failed"}
            else:
                msg = self.getMsg("error",field)
                return{"msg": msg, "result": "error"}
    #int-期望值范围
    def int_expected_range(self,field,require,value,ResultFromServer):
            begin = int(value.split("-")[0].encode('ascii'))
            end = int(value.split("-")[1].encode('ascii'))
            ResultFromServer=self.getFiled(ResultFromServer)
            if ResultFromServer.has_key(field):
                #print begin,end,int(ResultFromServer[field]),"这里是比较的范围"
                if begin<= int(ResultFromServer[field]) <= end:
                    msg = self.getMsg("success", field, require)
                    return {"msg": msg, "result": "success"}
                else:
                    msg = self.getMsg("failed", field, value=value, value2=str(ResultFromServer[field]))
                    return {"msg": msg, "result": "failed"}
            else:
                msg = self.getMsg("error", field)
                return {"msg": msg, "result": "error"}
    #int-期望值长度
    def int_expected_length(self,field,require,value,ResultFromServer):
        ResultFromServer = self.getFiled(ResultFromServer)
        if ResultFromServer.has_key(field):
            value = unicode_to_string(value)
            if str(type(ResultFromServer[field]))=="<type 'int'>":ResultFromServer[field]=str(ResultFromServer[field])
            if str(len(ResultFromServer[field]))==value:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=value, value2=str(len(ResultFromServer[field])))
                return {"msg": msg, "result": "failed"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}
    #int-string-期望值长度范围
    def int_expected_length_range(self,field,require,value,ResultFromServer):
        begin=int(value.split("-")[0])
        #print "这里是长度begin:",begin
        end=int(value.split("-")[1])
        ResultFromServer = self.getFiled(ResultFromServer)
        if ResultFromServer.has_key(field):
            if str(type(ResultFromServer[field])) == "<type 'int'>": ResultFromServer[field] = str(ResultFromServer[field])
            len2=len(ResultFromServer[field])
            #print "这里是长度len2222222,", len2,"being: ",begin," end: ",end
            #print begin<= len2 <= end,"比较结果"
            if begin<= len2 <= end:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=value, value2=str(len2))
                return {"msg": msg, "result": "failed"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}
    #int-模糊查找
    def int_fuzzy_search(self,field,require,value,ResultFromServer):
        strvalue=json.dumps(ResultFromServer)
        int_values = re.findall(r"\d+\.?\d*", strvalue)
        flag=False
        for val in int_values:
                if val == value:
                    flag=True
                    break;
        if flag:
            msg = self.getMsg("fuzzy_success", field,value=value)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("fuzzy_error", field, value=value)
            return {"msg": msg, "result": "failed"}
    #string - 等值匹配
    def string_equal_match(self,field,require,value,ResultFromServer):
        ResultFromServer = self.getFiled(ResultFromServer)
        if ResultFromServer.has_key(field):

            ResultFromServer[field] = unicode_to_string(ResultFromServer[field]);value=unicode_to_string(value)
            if ResultFromServer[field] == value:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=value, value2=ResultFromServer[field])
                return {"msg": msg, "result": "failed"}
        elif re.findall(r'\"%s\"\s*\:\s*\"%s\"' % (field, value), json.dumps(ResultFromServer, encoding='UTF-8', ensure_ascii=False)).__len__() !=0 :
            #print "这里找到了正则匹配值"
            msg = self.getMsg("success", field, require)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}
    #string-期望值长度
    def string_expected_length(self,field,require,value,ResultFromServer):
         return self.int_expected_length(field,require,value,ResultFromServer)
    #string - 模糊查找
    def string_fuzzy_search(self,field,require,value,ResultFromServer):
        # 模糊查找除了最基本的字段匹配，还需要另一个形式的全方位查找
        flag = False
        keyName = None
        #print "转化前",ResultFromServer
        ResultFromServer = self.getFiled(ResultFromServer)
       # print "转化后",ResultFromServer
        for key in ResultFromServer.keys():
            if str(type(ResultFromServer[key])) == "<type 'bool'>": continue;
            if str(type(ResultFromServer[key])) == "<type 'int'>": continue;
            if str(type(ResultFromServer[key])) == "<type 'unicode'>":
                result = str(ResultFromServer[key].encode('utf-8'))
            if str(type(ResultFromServer[key])) == "<type 'list'>":
                result = str(ResultFromServer[key])
            if str(type(ResultFromServer[key])) == "<type 'dict'>":
               result = str(ResultFromServer[key])
            #print "这里是最后的结果值被转化的字符串",result
            # print "这里是key",key
            # print "这是value",value.encode('utf-8'),type(value.encode('utf-8'))
            # print "这是result",json.dumps(result, ensure_ascii = False, encoding = 'utf-8'),type(result)
            # print '{"Coding":"1001","Name":"同程国际旅行社有限公司"}'==result
          #  print "成功者与失败者之间的比较"
            #  print value,type(value)
            #print "{\"Coding\": \"1001\", \"Name\": \"同程国际旅行社有限公司\"}".decode('utf-8')
           # print "比较结束",type("{\"Coding\": \"1001\", \"Name\": \"同程国际旅行社有限公司\"}".decode('utf-8'))
        #    hhh=json.dumps(ResultFromServer, encoding='UTF-8', ensure_ascii=False)
        #    print hhh
         #   print "{\"Coding\": \"1001\", \"Name\": \"同程国际旅行社有限公司\"}".decode('utf-8') in json.dumps(ResultFromServer, encoding='UTF-8', ensure_ascii=False).strip()
            #jhhh=re.findall(r"\d{4}-\d{2}-\d{2}", json.dumps(ResultFromServer, encoding='UTF-8', ensure_ascii=False))


        if (value in json.dumps(ResultFromServer, encoding='UTF-8', ensure_ascii=False)) and (flag == False):
            return {"msg": "全量匹配有效", "result": "success"}
        if flag:
            type2 = "success"
            msg = self.getMsg("success", field, require, value=keyName)
        else:
            msg = self.getMsg("error", field, value=value)
            type2 = "failed"
        return {"msg": msg, "result": type2}

    # 这边还少个普通的时间，但是目前没有数据，以后碰到再加
    #捕获时间戳
    def get_time_stamp(self,ResultFromServer):
        time_values = re.findall(r"\d{13}-\d+", json.dumps(ResultFromServer))
        times=[]
        if time_values:
            #print "捕获到符合时间戳的日期"
            for timevalue in time_values:
                newtime = timevalue.split("-")[0]
                ltime = time.localtime(int(newtime[:-3]))
                timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
                timeStr2=re.findall(r"\d{4}-\d{2}-\d{2}",timeStr)[0]
                times.append({"time_show":timeStr,"time_show_all":timeStr + "." + newtime[-3:],"time_show_normal":timeStr2})
        return times
    #普通时间的判定
    def match_normal_time(self,field,value,ResultFromServer):
        #print "开始普通匹配"
        #print value
        #print json.dumps(ResultFromServer)
        time_values = re.findall(r'\"%s\"\s*\:\s*\"%s\"' % (field,value), json.dumps(ResultFromServer))
        #print time_values,"这里是普通时间样式集合值"
        if(time_values.__len__()!=0):
            return True
        else:
            return False

    #date-等值匹配
    def data_equal_match(self,field,require,value,ResultFromServer):
        int_values=self.get_time_stamp(ResultFromServer)
        timeStr=""
        #判断期望值是否包含毫秒
        if "." in value:
            #包含小数点的
            timeStr = int_values[0]["time_show_all"]
        elif ":" in value:
            #不包含小数点的
            timeStr=int_values[0]["time_show"]
        else:
            timeStr = int_values[0]["time_show_normal"]

        if timeStr==value:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
        else:
                msg = self.getMsg("failed", field, value=value, value2=timeStr)
                return {"msg": msg, "result": "failed"}
    #date-期望值范围
    def data_expected_range(self,field,require,value,ResultFromServer):
        int_values = self.get_time_stamp(ResultFromServer)
        timeStr = ""
        # 判断期望值是否包含毫秒
        if "." in value:
            # 包含小数点的
            timeStr = int_values[0]["time_show_all"]
        elif ":" in value:
            # 不包含小数点的
            timeStr = int_values[0]["time_show"]
        else:
            timeStr = int_values[0]["time_show_normal"]
        if value.split(",")[0]<=timeStr<=value.split(",")[1]:
            msg = self.getMsg("success", field, require)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("failed", field, value=value, value2=timeStr)
            return {"msg": msg, "result": "failed"}
    #date-模糊查找
    def data_fuzzy_search(self,field,require,value,ResultFromServer):
        int_values = self.get_time_stamp(ResultFromServer)
        flag=self.match_normal_time(field,value,ResultFromServer)
        if flag:
            msg = self.getMsg("fuzzy_success", field, require, value=value)
            return {"msg": msg, "result": "success"}
        timeStr = []
        type="time_show_normal"
        if "." in value:type="time_show_all"
        elif ":" in value:type="time_show"
        else:type = "time_show_normal"
        # 判断期望值是否包含毫秒
        for time in int_values:
           timeStr.append(time[type])
        #print "这里是所有的被匹配到的时间数据",timeStr
        if value in timeStr:
            msg = self.getMsg("fuzzy_success", field, require,value=value)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("fuzzy_error", field, value=value)
            return {"msg": msg, "result": "failed"}
    #正则匹配
    def reg_match(self,field,require,value,ResultFromServer):
        strvalue = json.dumps(ResultFromServer)
        #print value,"这里是正则匹配表达式"
        results=re.findall(r''+value+'', strvalue)
        #print "这里是正则匹配的结果",results
        if results:
            msg = self.getMsg("success", field, require)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("failed", field, value=value,value2="返回值为空")
            return {"msg": msg, "result": "failed"}
    #bool-等值匹配
    def bool_equal_match(self,field,require,value,ResultFromServer):
        ResultFromServer = self.getFiled(ResultFromServer)
        if value.lower()=="true":
            value=True
        else:
            value=False
        if ResultFromServer.has_key(field):
            #print '这里是比较Bool',ResultFromServer[field],value,ResultFromServer[field]==value
            if ResultFromServer[field]==value:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=str(value), value2=str(ResultFromServer[field]))
                return {"msg": msg, "result": "failed"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}
    #[]-列表(数组)匹配
    #这个目前只做是否是数组的匹配
    def list_match(self,field,require,value,ResultFromServer):
        value=json.loads(value)
        ResultFromServer = self.getFiled(ResultFromServer)
        if str(type(value)) !="<type 'list'>":
            msg = self.getMsg("expect_field_error", field)
            return {"msg": msg, "result": "error"}
        if ResultFromServer.has_key(field):
            if type(ResultFromServer[field]) == type(value):
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=value, value2=ResultFromServer[field])
                return {"msg": msg, "result": "failed"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}
    #{}-字典(哈希)匹配
    def dict_match(self,field,require,value,ResultFromServer):
        value = json.loads(value)
        ResultFromServer = self.getFiled(ResultFromServer)
        if str(type(value)) != "<type 'dict'>":
            msg = self.getMsg("expect_field_error", field)
            return {"msg": msg, "result": "error"}
        if ResultFromServer.has_key(field):
            if type(ResultFromServer[field]) == type(value):
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
            else:
                msg = self.getMsg("failed", field, value=value, value2=ResultFromServer[field])
                return {"msg": msg, "result": "failed"}
        else:
            msg = self.getMsg("error", field)
            return {"msg": msg, "result": "error"}

    #response的其他属性
    def response_other(self,field,require,value,ResultFromServer):
        if value.isdigit():
            value=int(value)
        if value==ResultFromServer[field]:
                msg = self.getMsg("success", field, require)
                return {"msg": msg, "result": "success"}
        else:
                msg = self.getMsg("failed", field, value=value, value2=ResultFromServer[field])
                return {"msg": msg, "result": "failed"}

    #返回值为非json格式的验证：
    def non_json_format(self,field,require,value,ResultFromServer):
        if str(ResultFromServer).lower()==str(value).lower():
            msg = self.getMsg("success", field, require)
            return {"msg": msg, "result": "success"}
        else:
            msg = self.getMsg("failed", field, value=value, value2=ResultFromServer)
            return {"msg": msg, "result": "failed"}
