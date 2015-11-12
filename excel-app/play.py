

class CR(object):
    def writeLog(self):
        s = ' asdf asdf asdf asdf\n'
        s += ' asdf asdf asdf asdf\n'
        s += ' asdf asdf asdf asdf\n'
        s += ' asdf asdf asdf asdf\n'
        s += ' asdf asdf asdf asdf\n'
        
        log = open('log.txt','w')
        log.write(s)
        log.close()
        
        return
    
    def readLog(self):
        log = open('log.txt','r')
        s = log.read()
        log.close()
        print(s)
        
c = CR()
c.readLog()
        
