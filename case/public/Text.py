class TextView():
    @classmethod
    def Print(self,msg):
        print msg
    @classmethod
    def success(self,msg):
        print "\033[0;32;48m%s\033[0m" %(msg)
    @classmethod
    def error(self,msg):
        print "\033[0;31;48m%s\033[0m" % (msg)
