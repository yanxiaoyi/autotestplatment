# -*- coding:utf-8 -*-
from app.sql import querySQL
import json
import re
import time
from case.public.Text import TextView

class UserInfo:
    def __init__(self):
        try:
            self.con = querySQL.MYSQL('10.100.156.202', '******', '*****',
                                      '*******', 3500)
            self.userlist=self.getUserList()
            TextView.success("用户表加载完成...")
        except Exception,e:
            TextView.error("用户表加载失败...")
    def getUserList(slef):
        sql = "SELECT * From system_public_users"
        res =slef.con.query(sql)
        userlist = {}
        for user in res:
            userlist[user[2]] = {"userName": user[1], "userIp": user[2]}
        return userlist

    def getUser(self,hash):
        ip=str(hash["ip"])
        if self.userlist.has_key(ip):
            return self.userlist[ip]
        else:
            return {"userName":ip}
