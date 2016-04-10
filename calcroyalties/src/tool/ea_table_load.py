import xml.etree.ElementTree as ET

from xml.etree import ElementTree
from xml.dom import minidom

class EA_Tables (object):

    def __init__(self):

        self.root = ET.Element('XMI')
        self.root.set('xmi.version', '1.2')
        self.root.set('xmlns:UML', 'org.omg/UML/1.4')
        e = ET.SubElement(self.root, 'XMI.content')
        e = ET.SubElement(e, 'UML:Model')
        e.set('xmi.id', 'M.1')
        e.set('name', 'Lorraine')
        e = ET.SubElement(e, 'UML:Namespace.ownedElement')

        t = ET.SubElement(e, 'UML:Class')
        t.set('xmi.id', 'C.1')
        t.set('name', 'LorraineTable')

        t = ET.SubElement(t, 'UML:Classifier.feature')

        a = ET.SubElement(t, 'UML:Attribute')
        a.set('xmi.id', 'A.1')
        a.set('name', 'Name')

        a = ET.SubElement(t, 'UML:Attribute')
        a.set('xmi.id', 'A.2')
        a.set('name', 'Street')

        a = ET.SubElement(t, 'UML:Attribute')
        a.set('xmi.id', 'A.3')
        a.set('name', 'Zip')

    def prettify(self):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(self.root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

# UML:Model

ea = EA_Tables()


# print(ea.prettify())
