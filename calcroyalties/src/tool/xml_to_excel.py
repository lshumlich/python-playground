#!/bin/env python3
"""
This is responsible for converting xml data files into to excel. We then will
load the excel into sql tables.

As of today this is just a hack file

"""

import config
# import xml
from openpyxl import Workbook

import xml.etree.ElementTree as et

# tree = et.parse('\\$temp\\xml\\Sample-FACILITY.xml')
# tree = et.parse('\\$temp\\xml\\Sample-VOLUMETRIC.xml')
tree = et.parse(config.get_temp_dir() + 'Sample-FACILITY.xml')

root = tree.getroot()

# print ('---Tag-->', root.tag)
# print('----attr->', root.attrib)
#
# for c in root.iter():
#     print(c.tag, " - ", c.attrib, c.text, ' - ' )


class CommonData():
    eDocument = {}
    eRow = {}
    column_count = 0
    dot_notation = []
    data = []



def showStruc(element, level):
    for child in element:
        if '}' in child.tag:
            tag = child.tag.split('}', 1)[1]  # strip all namespaces
        else:
            tag = child.tag

        if len(cd.dot_notation) <= level:
            cd.dot_notation.append("")

        cd.dot_notation[level] = tag
        fulltag = ""
        for i in range(level+1):
            fulltag += '.' + cd.dot_notation[i]

        print(level, ' - ', fulltag, " Tag-> ", tag, "Child-> ", child.attrib, child.text)

        if fulltag not in cd.eDocument:
            # print("   new element: ", fulltag, cd.column_count)
            cd.eDocument[fulltag] = cd.column_count
            cd.column_count += 1
        if fulltag not in cd.eRow:
            cd.eRow[fulltag] = cd.column_count
            cd.data.append(child.text)
        else:
            print("---> output row: ", cd.data)


        showStruc(child, level + 1)

def show_children(e):
    for child in e:
        print("child-->", child.tag)



def write_excel():
    print("About to write some excel.")
    wb = Workbook()
    ws = wb.active
    ws1 = wb.create_sheet("Mysheet")
    ws1.cell(row=1, column=1, value=12345)
    wb.save(config.get_temp_dir() + 'lfsdata.xlsx')


write_excel()

#
#
# cd = CommonData()
#
# # showStruc(root, 0)
# ns = {'soap':'http://schemas.xmlsoap.org/soap/envelope/'}
# e = root
# e = e.find('soap:Body', ns)
# e = e.find('LIST_FACILITY_003')
# e = e.find('DATAAREA')
# print('length:',len(e))
# print('data-->',e[0].tag, e[1].tag)
# print('data-->',e[0][0].tag, e[1][0].tag)
# show_children(e)

# for child in root:
#     print("Tag-> ", child.tag, "Child-> ", child.attrib)
#     # r = child.getroot()
#     # print ("r-->", r.tag)
#     for c in child:
#         print("T-> ", c.tag, "C- > ", c.attrib)


