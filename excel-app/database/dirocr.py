"""
This uses one or more dos "Directory Listing" created using the dos command "dir > dir.txt"

It creates a index html type page to make finding documents much easier.

Again not pretty but functional 

"""

import re
import urllib.request as req

header1 = """
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
.newspaper {
    -webkit-columns: 150px 9; /* Chrome, Safari, Opera */
    -moz-columns: 150px 9; /* Firefox */
    columns: 150px 9;
}
table.print-friendly tr td, table.print-friendly tr th {
    page-break-inside: avoid;
}
</style>
</head>
<body>
"""
headerLease = """
<h1>Directory List by Lease</h1>
<p><strong>Note:</strong>Does not work with IE. <b>Hint:</b> Press {Ctrl}f to find a specific lease. <a href="$IndexByArea.html">By Area</a></p>
"""
headerArea = """
<h1>Directory List by Area</h1>
<p><strong>Note:</strong>Does not work with IE. <b>Hint:</b> Press {Ctrl}f to find a specific lease. <a href="$IndexByLease.html">By Lease</a></p>
"""
header3 = """
<div class="newspaper">
"""
footer1 = """
</div>
</body>
</html>
"""

class ds(object):
    def __init__(self, lease, area, fileName, pathName):
        self.lease = lease
        self.area = area
        self.fileName = fileName
        self.pathName = pathName
    def __repr__(self):
        return repr((self.lease, self.area, self.fileName, self.pathName))
    
def loadDir(fName,dirList):
    dateP = re.compile('\d{2}/\d{2}/\d{4}')
    leaseP = re.compile('[A-Z]{2}-\d{4}')
    areaP = re.compile('LEASE_-_.+.PDF',re.I)
    pathName = None
    with open (fName,'r') as dirf:
        for line in dirf:
            m = dateP.search(line)
            if m != None and m.start() == 0:
                if line[24:29] == '<DIR>':
                    None
                else:
                    try:
                        fileName = line[39:].strip()
                        m = leaseP.search(fileName)
                        lease = m.group()
                        m = areaP.search(fileName)
                        area = m.group()[8:-4]
                        dirList.append(ds(lease,area,fileName,pathName))
                    except Exception as e:
                        print (e)
                        print (fileName)
                        raise e
            elif line[0:10] == ' Directory':
                pathName = line[14:].strip()

def outputHtmlByLease(fileName,dirList):

    html = open(fileName,'w')
    html.write(header1)
    html.write(headerLease)
    html.write(header3)
    html.write('<ul>\n')
    for o in dirList:
        html.write('<li><a href="file:' + req.pathname2url(o.pathName + '\\' + o.fileName) + '"  title="' + o.area + '" target="_blank">' + o.lease + ' </a></li>\n')
    html.write('</ul>\n')
    html.write(footer1)
    html.close()

def outputHtmlByArea(fileName,dirList):

    html = open(fileName,'w')
    html.write(header1)
    html.write(headerArea)
    html.write(header3)
    area=None
    for o in dirList:
        if area != o.area:
            if area != None:
                html.write('</ul>\n')
                html.write('</td></tr>\n')
                html.write('</table>\n')
            area = o.area
            html.write('<table class="print-friendly" style="width:100%">\n')
            html.write('<tr><td><b>'+area.replace('_',' ')+'</b></td></tr>\n')
            html.write('<tr><td>\n')
            html.write('<ul>\n')
        html.write('<li><a href="file:' + req.pathname2url(o.pathName+'\\' + o.fileName) + '"  title="' + o.area + '" target="_blank">' + o.lease + ' </a></li>\n')
    html.write('</ul>\n')
    html.write('</td></tr>\n')
    html.write('</table>\n')
    html.write(footer1)
    html.close()

if __name__ == '__main__':
    dirList = []
    loadDir('dir - CR-O&G AGREEMENTS.txt',dirList)
    loadDir("dir - PDF's - Scanned to Update Missing Leases.txt",dirList)
    loadDir("dir - PDF's - Newly Scanned.txt",dirList)
    
       
    dirList = sorted(dirList, key=lambda o: o.lease)
    outputHtmlByLease('$IndexByLease.html',dirList)
    
    dirList = sorted(dirList, key=lambda o: o.area)
    outputHtmlByArea('$IndexByArea.html',dirList)
    
