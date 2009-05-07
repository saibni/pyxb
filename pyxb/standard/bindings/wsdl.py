from pyxb.standard.bindings.raw.wsdl import *
import pyxb.standard.bindings.raw.wsdl as raw_wsdl

import pyxb.Namespace
import pyxb.utils.domutils as domutils

class _WSDL_Binding_mixin (object):
    """Mix-in class to mark transport-specific elements that appear in
    WSDL binding elements."""
    pass

class tPort (raw_wsdl.tPort):
    def bindingReference (self):
        return self.__bindingReference
    def setBindingReference (self, binding_reference):
        self.__bindingReference = binding_reference
    __bindingReference = None
raw_wsdl.tPort._SetClassRef(tPort)

class tBinding (raw_wsdl.tBinding):
    def portTypeReference (self):
        return self.__portTypeReference
    def setPortTypeReference (self, port_type_reference):
        self.__portTypeReference = port_type_reference
    __portTypeReference = None
raw_wsdl.tBinding._SetClassRef(tBinding)

class definitions (raw_wsdl.definitions):
    def messageMap (self):
        return self.__messageMap
    __messageMap = None

    def namespaceData (self):
        return self.__namespaceData
    __namespaceData = None

    def bindingMap (self):
        return self.__bindingMap

    def targetNamespace (self):
        return self.namespaceData().targetNamespace()

    def _addToMap (self, map, qname, value):
        map[qname] = value
        (ns, ln) = qname
        if (ns == self.targetNamespace()):
            map[(None, ln)] = value
        elif (ns is None):
            map[(self.targetNamespace(), ln)] = value
        return map

    @classmethod
    def CreateFromDOM (cls, node, *args, **kw):
        # Get the target namespace and other relevant information, and set the
        # per-node in scope namespaces so we can do QName resolution.
        ns_data = domutils.NamespaceDataFromNode(node)
        rv = super(definitions, cls).CreateFromDOM(node, *args, **kw)
        rv.__namespaceData = ns_data
        rv.__buildMaps()
        return rv

    def __buildMaps (self):
        self.__messageMap = { }
        for m in self.message():
            name_qname = domutils.InterpretQName(m._domNode(), m.name())
            self._addToMap(self.__messageMap, name_qname, m)
            print 'Message: %s' % (name_qname,)
        self.__portTypeMap = { }
        for pt in self.portType():
            port_type_qname = domutils.InterpretQName(pt._domNode(), pt.name())
            self._addToMap(self.__portTypeMap, port_type_qname, pt)
            print 'Port type: %s' % (port_type_qname,)
        self.__bindingMap = { }
        for b in self.binding():
            binding_qname = domutils.InterpretQName(b._domNode(), b.name())
            self._addToMap(self.__bindingMap, binding_qname, b)
            print 'Binding: %s' % (binding_qname,)
            port_type_qname = domutils.InterpretQName(b._domNode(), b.type())
            b.setPortTypeReference(self.__portTypeMap[port_type_qname])
        self.__serviceMap = { }
        for s in self.service():
            service_qname = domutils.InterpretQName(s._domNode(), s.name())
            self._addToMap(self.__serviceMap, service_qname, s)
            port_map = { }
            for p in s.port():
                port_qname = domutils.InterpretQName(p._domNode(), p.name())
                port_map[port_qname] = p
                print 'Service %s port: %s' % (service_qname, port_qname)
                binding_qname = domutils.InterpretQName(p._domNode(), p.binding())
                p.setBindingReference(self.__bindingMap[binding_qname])

    def findPort (self, module):
        for s in self.service():
            for p in s.port():
                for wc in p.wildcardElements():
                    if isinstance(wc, pyxb.binding.basis.element):
                        if wc._Namespace == module.Namespace:
                            return (s, p, wc)
                    else:
                        if wc.namespaceURI == module.Namespace.uri():
                            # This shouldn't happen: if we have the module,
                            # its namespace should have the module registered,
                            # in which case when we created the raw_wsdl document
                            # we'd have been able to create a Python instance
                            # for the wildcard rather than leave it as a DOM
                            # instance.
                            return (s, p, module.CreateFromDOM(wc))
        return None

    def findPortType (self, port):
        for pt in self.portType():
            if pt.name() == port.name():
                return pt
        return None

raw_wsdl.definitions._SetClassRef(definitions)