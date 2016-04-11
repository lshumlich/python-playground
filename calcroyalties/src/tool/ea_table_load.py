import xml.etree.ElementTree as ET

from xml.etree import ElementTree
from xml.dom import minidom

import config

class EA_Tables (object):

    def __init__(self):
        self.table_count = 0
        self.attribute_count = 0

        self.root = ET.Element('XMI')
        self.root.set('xmi.version', '1.2')
        self.root.set('xmlns:UML', 'org.omg/UML/1.4')
        e = ET.SubElement(self.root, 'XMI.content')
        e = ET.SubElement(e, 'UML:Model')
        e.set('xmi.id', 'M.1')
        e.set('name', 'Lorraine')
        self.element = ET.SubElement(e, 'UML:Namespace.ownedElement')

    def table(self,table):
        self.table_count += 1
        t = ET.SubElement(self.element, 'UML:Class')
        t.set('xmi.id', 'C.' + str(self.table_count))
        t.set('name', table)

        self.tab = ET.SubElement(t, 'UML:Classifier.feature')

    def attribute(self,attribute):
        self.attribute_count += 1

        a = ET.SubElement(self.tab, 'UML:Attribute')
        a.set('xmi.id', 'A.' + str(self.attribute_count))
        a.set('name', attribute)

    def prettify(self):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(self.root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

# UML:Model

ea = EA_Tables()

dbi = config.get_database_instance()

tables = dbi.get_table_names()
for t in tables:
    ea.table(t)

    c = dbi.execute("PRAGMA table_info(" + t + ");")

    for row in c:
        ea.attribute(row[1])
        # print(row,row[1],row[2])

txt = ea.prettify()

f = open(config.get_temp_dir() + 'ea.xml', 'w')
f.write(txt)
f.close()

print(txt)
