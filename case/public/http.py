# -*- coding:utf-8 -*-
import requests
class Http:
    def __init__(self,url,timeout,hash,interface):
        self.url=url
        self.timeout=timeout
        self.hash=hash
        self.interface=interface


    def post(self):
        kwargs = {
            'headers': {'CName': 'automation', 'PLevel': '5', 'CIP': '127.0.0.1', 'APIName': self.interface}
        }
        res = requests.post(
             url=self.url, json=self.hash,timeout=self.timeout, **kwargs)
        
        hash={"content":res.content,"other":{"status_code":res.status_code}}
        try:
            if res.text==None:
                hash["other"]["text"]=""
            else:
                hash["other"]["text"] = res.text
            
            return hash
        except Exception,e:
            print str(e);
            return  {"content":res.content,"other":{"status_code":""}}

    def get(self):
        kwargs = {
            'headers': {'CName': 'automation', 'PLevel': '5', 'CIP': '127.0.0.1', 'APIName': self.interface}
        }
        
        res = requests.get(url=self.url,params=self.hash,**kwargs)
        hash = {"content": res.content, "other": {"status_code": res.status_code}}
        try:
            if res.text==None:
                hash["other"]["text"]=""
            else:
                hash["other"]["text"] = res.text
            return hash
        except Exception,e:
            print str(e);
            return  {"content":res.content,"other":{"status_code":""}}
