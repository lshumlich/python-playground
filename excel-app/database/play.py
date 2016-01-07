import re
import urllib.request as req

text = """
"3.0 ROYALTY 
3.1 Subject to clause 3.2, the gross royalty on Oil or Gas and Products produced from or attributable to the Lease Lands shall be calculated in accordance with this Appendix, and the attached Exhibit 'A"". 
3.2 Royalty on Condensate shall be calculated in accordance with the Pentanes Plus royalty prescribed in this Lease.
A. OIL ROYALTY The gross royalty for Oil shall be the Oil Royalty Rate multiplied by the Oil Price multiplied by the Oil Royalty Production for that month, where;
Oil Royalty Rate means 1.0 times the prevailing Province of Saskatchewan Crown Oil Royalty rate for fourth tier oil as prescribed by the Crown Royalty Legislation [without reference to royalty holidays or other special incentives]; 
The net royalty payable on Oil shall be the gross royalty on the Oil less the Trucking Costs for Oil. 
B. GAS ROYALTY 
The gross royalty for Gas shall be the Gas Production for that month multiplied by the Gas Royalty Rate multiplied by the Gas Price for that month, where; 
Gas Royalty Rate means 1.0 times the prevailing Province of Saskatchewan Crown Royalty rate for fourth tier gas, as prescribed by the Crown Royalty Legislation, [without reference to royalty holidays or other special incentives]; 
The net royalty payable on Gas shall be the gross royalty on Gas less the Gas Cost Allowance.
Notwithstanding clause 4.0 in Appendix ""B"" - Royalty Terms, the Authorized Deduction for Gas Cost Allowance will be as per the Saskatchewan Crown Royalty Legislation to a maximum of $10.00/10 3m3 [ten dollars per thousand cubic metres]."
"""



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

s = 'asdf asdf asdf sadf Oil Royalty Rate means 1.0 times the prevailing '

p = re.compile('oil royalty rate means ([0-9.]+) times', re.I)
print(s)
print(p)
m = p.search(s)
print(m)
print(m.group(0))
print(m.group(1))
t = float(m.group(1))
x = t * 3
print(x)
print('-----')

s = '''
<div id=hotlinklist>
<a href="foo1.com">Foo1</a>
  <div id=hotlink>
    <a href="/">Home</a>
  </div>
  <div id=hotlink>
    <a href="/extract">Extract</a>
  </div>
  <div id=hotlink>
    <a href="/sitemap">Sitemap</a>
  </div>
</div>'''
m = re.compile(r'<a href="/sitemap">(.*?)</a>').search(s)
print(m)
print(m.group(0))
print(m.group(1))

