#!/usr/bin/env/python
# -*- coding: utf-8 -*-

###
### Author:  Chris Iatrou (ichrispa@core-vector.net)
### Version: rev 13
###
### This program was created for educational purposes and has been
### contributed to the open62541 project by the author. All licensing
### terms for this source is inherited by the terms and conditions
### specified for by the open62541 project (see the projects readme
### file for more information on the LGPL terms and restrictions).
###
### This program is not meant to be used in a production environment. The
### author is not liable for any complications arising due to the use of
### this program.
###

from nodes import *
from backend_open62541_datatypes import *

def generateReferenceCode(reference):
    if reference.isForward:
        return "UA_Server_addReference(server, %s, %s, %s, true);" % \
            (generateNodeIdCode(reference.source), \
             generateNodeIdCode(reference.referenceType), \
             generateExpandedNodeIdCode(reference.target))
    else:
      return "UA_Server_addReference(server, %s, %s, %s, false);" % \
          (generateNodeIdCode(reference.source), \
           generateNodeIdCode(reference.referenceType), \
           generateExpandedNodeIdCode(reference.target))

def generateReferenceTypeNodeCode(node):
    code = []
    code.append("UA_ReferenceTypeAttributes attr;")
    code.append("UA_ReferenceTypeAttributes_init(&attr);")
    if node.isAbstract:
        code.append("attr.isAbstract = true;")
    if node.symmetric:
        code.append("attr.symmetric  = true;")
    if node.inverseName != "":
        code.append("attr.inverseName  = UA_LOCALIZEDTEXT_ALLOC(\"en_US\", \"%s\");" % \
                    node.inverseName)
    return code;

def generateObjectNodeCode(node):
    code = []
    code.append("UA_ObjectAttributes attr;")
    code.append("UA_ObjectAttributes_init(&attr);")
    if node.eventNotifier:
        code.append("attr.eventNotifier = true;")
    return code;

def generateVariableNodeCode(node):
    code = []
    code.append("UA_VariableAttributes attr;")
    code.append("UA_VariableAttributes_init(&attr);")
    if node.historizing:
        code.append("attr.historizing = true;")
    code.append("attr.minimumSamplingInterval = %f;" % node.minimumSamplingInterval)
    code.append("attr.userAccessLevel = %d;" % node.userAccessLevel)
    code.append("attr.accessLevel = %d;" % node.accessLevel)
    code.append("attr.valueRank = %d;" % node.valueRank)
    if node.value:
        if isinstance(node.value, list):
            values = [generateValueRepresentation(x) for x in node.value]
            typename = type(node.value[0]).__name__
            code.append(("UA_%s value[%s] = {" + ",".join(values) + "};") % (typename, len(node.value)))
            code.append("UA_Variant_setArray(&attr.value, (void*)value, %s, &UA_TYPES[UA_TYPES_%s]);" % (str(len(values)), typename.upper()))
        else:
            typename = type(node.value).__name__
            code.append(("UA_%s value = " + generateValueRepresentation(node.value) + ";") % typename)
            code.append("UA_Variant_setScalar(&attr.value, &value, &UA_TYPES[UA_TYPES_%s]);" % typename.upper())
    return code

def generateVariableTypeNodeCode(node):
    code = []
    code.append("UA_VariableTypeAttributes attr;")
    code.append("UA_VariableTypeAttributes_init(&attr);")
    if node.historizing:
        code.append("attr.historizing = true;")
    code.append("attr.valueRank = (UA_Int32)%s;" %str(node.valueRank))
    return code

def generateMethodNodeCode(node):
    code = []
    code.append("UA_MethodAttributes attr;")
    code.append("UA_MethodAttributes_init(&attr);")
    if node.executable:
      code.append("attr.executable = true;")
    if node.userExecutable:
      code.append("attr.userExecutable = true;")
    return code

def generateObjectTypeNodeCode(node):
    code = []
    code.append("UA_ObjectTypeAttributes attr;")
    code.append("UA_ObjectTypeAttributes_init(&attr);")
    if node.isAbstract:
      code.append("attr.isAbstract = true;")
    return code

def generateDataTypeNodeCode(node):
    code = []
    code.append("UA_DataTypeAttributes attr;")
    code.append("UA_DataTypeAttributes_init(&attr);")
    if node.isAbstract:
      code.append("attr.isAbstract = true;")
    return code

def generateViewNodeCode(node):
    code = []
    code.append("UA_ViewAttributes attr;")
    code.append("UA_ViewAttributes_init(&attr);")
    if node.containsNoLoops:
      code.append("attr.containsNoLoops = true;")
    code.append("attr.eventNotifier = (UA_Byte)%s;" % str(node.eventNotifier))
    return code

def generateNodeCode(node, supressGenerationOfAttribute, generate_ns0, parentrefs):
    code = []
    code.append("{")

    if isinstance(node, ReferenceTypeNode):
        code.extend(generateReferenceTypeNodeCode(node))
    elif isinstance(node, ObjectNode):
        code.extend(generateObjectNodeCode(node))
    elif isinstance(node, VariableNode) and not isinstance(node, VariableTypeNode):
        code.extend(generateVariableNodeCode(node))
    elif isinstance(node, VariableTypeNode):
        code.extend(generateVariableTypeNodeCode(node))
    elif isinstance(node, MethodNode):
        code.extend(generateMethodNodeCode(node))
    elif isinstance(node, ObjectTypeNode):
        code.extend(generateObjectTypeNodeCode(node))
    elif isinstance(node, DataTypeNode):
        code.extend(generateDataTypeNodeCode(node))
    elif isinstance(node, ViewNode):
        code.extend(generateViewNodeCode(node))

    code.append("attr.displayName = " + generateLocalizedTextCode(node.displayName) + ";")
    code.append("attr.description = " + generateLocalizedTextCode(node.description) + ";")
    code.append("attr.writeMask = %d;" % node.writeMask)
    code.append("attr.userWriteMask = %d;" % node.userWriteMask)
    
    code.append("UA_Server_add%s_begin(server," % node.__class__.__name__)
    code.append(generateNodeIdCode(node.id) + ",")
    code.append(generateQualifiedNameCode(node.browseName) + ",")
    code.append("attr,")
    if isinstance(node, MethodNode):
        code.append("NULL, NULL,")
    code.append("NULL);")
    code.append("}\n")
    return "\n".join(code)
