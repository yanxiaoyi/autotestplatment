# -*- coding: UTF-8 -*-
import pymysql
# 连接数据库
class MYSQL:
    def __init__(self, host, user, pwd, db, port):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.port = port

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "没有配置数据库")
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, port=self.port, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "数据库连接失败")
        else:
            return cur

    def ExecQuery(self, sql):
        """
               ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        """

        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        resList = cur.fetchall()
        self.conn.close()
        return resList

    def Close(self,):
        self.conn.close()

