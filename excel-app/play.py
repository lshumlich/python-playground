import re
import urllib.request as req

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
        
# c = CR()
# c.readLog()
#
# Example 1
#
t='0----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8'
s='asdf asdf asdf# sadfasdf 1234.56. asf asf 23 asdf'
p = re.compile('[\d.]+')
print(p)
m = p.search(s)
print(m)
print("Group:'"+m.group()+"'")
print("Start:'",m.start(),"'")
print("End:'",m.end(),"'")

#
# Example 2
#
print ("Exampl 2")
t='0----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8'
s='asdf asdf asdf# sad LS-1234 fasdf 1234.56. as-f asf 23 a LS-sdf'
p = re.compile('\s[A-Z]{2,2}-\d{4,4}\s')
print(p)
m = p.search(s)
print(m)
if m != None:
    print("Group:'"+m.group()+"'")
    print("Start:'",m.start(),"'")
    print("End:'",m.end(),"'")
#
# Example 2
#
print ("Exampl 3")
t='0----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8'
s='asdf asdf asdf# sad LS-1234 fasdf 1234.56. as-f asf 23 a LS-sdf'
p = re.compile('56.+23')
print(p)
m = p.search(s)
print(m)
if m != None:
    print("Group:'"+m.group()+"'")
    print("Start:'",m.start(),"'")
    print("End:'",m.end(),"'")
    
print()
query = '#$%asdf-_+.txt'
q = req.pathname2url(query)
print (q)
