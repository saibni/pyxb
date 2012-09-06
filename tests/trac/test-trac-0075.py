# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb.binding.generate
import pyxb.binding.datatypes as xs
import pyxb.binding.basis
import pyxb.binding.content
import pyxb.utils.domutils
import xml.dom.minidom

import os.path
xsd='''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:simpleType name="tInner">
  <xs:restriction base="xs:string"/>
</xs:simpleType>
<xs:complexType name="tTop">
  <xs:sequence>
    <xs:element name="inner" type="tInner"/>
  </xs:sequence>
</xs:complexType>
<xs:element name="top" type="tTop"/>
</xs:schema>'''

#file('schema.xsd', 'w').write(xsd)
code = pyxb.binding.generate.GeneratePython(schema_text=xsd)
#file('code.py', 'w').write(code)
#print code

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb.exceptions_ import *

import unittest

class TestTrac_0075 (unittest.TestCase):
    def setUp (self):
        # Prepare to hide warnings about failure to convert DOM node to binding
        self.__basis_log = logging.getLogger('pyxb.binding.basis')
        self.__basis_loglevel = self.__basis_log.level

    def tearDown (self):
        self.__basis_log.level = self.__basis_loglevel

    def testGood (self):
        xmls = '<top><inner>content</inner></top>'
        instance = CreateFromDocument(xmls)
        self.assertEqual('content', instance.inner)

    def testUnrecognizedElementError (self):
        xmls = '<t0p><inner>content</inner></t0p>'
        try:
            instance = CreateFromDocument(xmls)
            self.fail("Succeeded in creating from document with bad top level element")
        except UnrecognizedElementError, e:
            self.assertEqual('t0p', e.element_name)

    def testNotAnElementError (self):
        elt = tTop._UseForTag('inner')
        self.assertTrue(isinstance(elt, pyxb.binding.content.ElementDeclaration))
        try:
            elt = tTop._UseForTag('notInner')
            self.fail('Found non-existent inner element')
        except NotAnElementError, e:
            self.assertEqual('notInner', e.element_name)
            self.assertEqual(tTop, e.containing_type)

    def testUnrecognizedContentError (self):
        # Hide the warnings that tInner could not be converted to binding
        self.__basis_log.setLevel(logging.ERROR)
        tag = Namespace.createExpandedName('tInner')
        xmls = '<top><tInner>content</tInner></top>'
        try:
            instance = CreateFromDocument(xmls)
            self.fail("Succeeded in creating from document with bad inner element")
        except UnrecognizedContentError, e:
            if isinstance(e.content, xml.dom.Node):
                self.assertEqual(e.content.localName, tag.localName())
            else:
                self.assertEqual(tag, e.content.name)
                loc = e.content.location
                self.assertEqual(1, loc.lineNumber)
                self.assertEqual(5, loc.columnNumber)

        dom = xml.dom.minidom.parseString(xmls)
        try:
            instance = CreateFromDOM(dom)
            self.fail("Succeeded in creating from document with bad inner element")
        except UnrecognizedContentError, e:
            self.assertEqual(dom.documentElement.firstChild, e.content)

    '''
    NOT YET FINISHED

    def testExtraContentError (self):
        self.fail("Unimplemented test")

    def testMissingContentError (self):
        self.fail("Unimplemented test")

    def testUnrecognizedAttributeError (self):
        self.fail("Unimplemented test")
    '''

if __name__ == '__main__':
    unittest.main()
