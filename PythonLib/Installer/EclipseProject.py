#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
import xml.etree.ElementTree as ET 

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class EclipseProject(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self, Installer, Encoder):
    #==========================================
        super(EclipseProject, self).__init__()
        
        self.Installer = Installer
        self.Encoder   = Encoder 
        
        
    #==========================================
    def setProjectName(self, EclProjectName):
    #==========================================
        self.EclProjectName = EclProjectName
    
        FN_cproject = self.Installer.CMakeBuildDir + "/.project"
        assertFileExists(FN_cproject, ".project not found")
        
        Tree = ET.parse(FN_cproject)
        Root = Tree.getroot()
            
        Element0 = Root[0]
        assert(Element0.tag == "name")
        Element0.text = self.EclProjectName
        
        Tree.write(FN_cproject, encoding='utf-8', xml_declaration=True)

    #==========================================
    def setAttr(self, Parent, EclKey, EclValue):
    #==========================================
        Element = self.findElement(Parent, EclKey)
        Element.set("value", EclValue)
        
    #==========================================
    def setListAttr(self, Parent, EclKey, EclValue):
    #==========================================
        Element = self.findElement(Parent, EclKey)
        assert(len(Element) == 1)
        Element.find("listEntry").set("value", EclValue)
        
        #Element.set("value", EclValue)
                    
    #==========================================
    def findElement(self, Parent, EclKey):
    #==========================================
        for Element in Parent:
            for (AttrName, AttrValue) in Element.items():
                # "Attribute Key" and "Attribute Value": XML terminology
                # "Key" and "Value": names that Eclipse defines (we have some collision here)
                if AttrName == "key" and AttrValue == EclKey:
                    return Element
        assert(0), "Element not found"
    
    #==========================================
    def create_LaunchConfiguration(self, DstDir):
    #==========================================
        Tree = ET.ElementTree(ET.fromstring(self.Template_LaunchFile))
        Root = Tree.getroot()
        
        
        ProgramArguments = self.Encoder.get_CommandLineArguments()
        ProgramName      = self.Encoder.EncBin
        ProjectAttribute = self.EclProjectName #eclipse project that this launch file belongs to (name as shown in explorer!)
        WorkingDir       = self.Encoder.OutputDir  #output directory
        
        #-------------------------------------
        # CHANGING TEMPLATE
        #-------------------------------------
        self.setAttr(Root, "org.eclipse.cdt.launch.PROGRAM_ARGUMENTS", ProgramArguments)
        self.setAttr(Root, "org.eclipse.cdt.launch.PROGRAM_NAME", ProgramName)
        self.setAttr(Root, "org.eclipse.cdt.launch.PROJECT_ATTR", ProjectAttribute) 
        self.setAttr(Root, "org.eclipse.cdt.launch.WORKING_DIRECTORY", WorkingDir)
    
        self.setListAttr(Root, "org.eclipse.debug.core.MAPPED_RESOURCE_PATHS", "/HARP")
    
        LaunchConfig_FN = DstDir + "/" + self.EclProjectName + " Configuration.launch"
        Tree.write(LaunchConfig_FN, encoding='utf-8', xml_declaration=True)    
    

    
    Template_LaunchFile = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<launchConfiguration type="org.eclipse.cdt.launch.applicationLaunchType">
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.AUTO_SOLIB" value="true"/>
<listAttribute key="org.eclipse.cdt.dsf.gdb.AUTO_SOLIB_LIST"/>
<stringAttribute key="org.eclipse.cdt.dsf.gdb.DEBUG_NAME" value="gdb"/>
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.DEBUG_ON_FORK" value="false"/>
<stringAttribute key="org.eclipse.cdt.dsf.gdb.GDB_INIT" value=".gdbinit"/>
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.NON_STOP" value="false"/>
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.REVERSE" value="false"/>
<listAttribute key="org.eclipse.cdt.dsf.gdb.SOLIB_PATH"/>
<stringAttribute key="org.eclipse.cdt.dsf.gdb.TRACEPOINT_MODE" value="TP_NORMAL_ONLY"/>
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.UPDATE_THREADLIST_ON_SUSPEND" value="false"/>
<booleanAttribute key="org.eclipse.cdt.dsf.gdb.internal.ui.launching.LocalApplicationCDebuggerTab.DEFAULTS_SET" value="true"/>
<intAttribute key="org.eclipse.cdt.launch.ATTR_BUILD_BEFORE_LAUNCH_ATTR" value="2"/>
<stringAttribute key="org.eclipse.cdt.launch.COREFILE_PATH" value=""/>
<stringAttribute key="org.eclipse.cdt.launch.DEBUGGER_ID" value="gdb"/>
<stringAttribute key="org.eclipse.cdt.launch.DEBUGGER_START_MODE" value="run"/>
<booleanAttribute key="org.eclipse.cdt.launch.DEBUGGER_STOP_AT_MAIN" value="false"/>
<stringAttribute key="org.eclipse.cdt.launch.DEBUGGER_STOP_AT_MAIN_SYMBOL" value="main"/>
<stringAttribute key="org.eclipse.cdt.launch.PROGRAM_ARGUMENTS" value="--HARP_ObsPOCs=0,1,2,3,4,5&#10;--HARP_ObsCTUs=14&#10;--HARP_PUs &#10;--HARP_TmpDir=tmp&#10;--HARP_CG_Callgraph&#10;-i ../LMS/YUVs/LMS_640x360.yuv -wdt 640 -hgt 360&#10;-f 6 -c ../HM/cfg/encoder_lowdelay_P_main.cfg  --QP=10 -b tmp/str.bin  -fr 2 --InputBitDepth=8"/>
<stringAttribute key="org.eclipse.cdt.launch.PROGRAM_NAME" value="/home/dom/Desktop/Jetson_TK1/HARP/bin/HM_HARP/TAppEncoder"/>
<stringAttribute key="org.eclipse.cdt.launch.PROJECT_ATTR" value="HARP"/>
<booleanAttribute key="org.eclipse.cdt.launch.PROJECT_BUILD_CONFIG_AUTO_ATTR" value="true"/>
<stringAttribute key="org.eclipse.cdt.launch.PROJECT_BUILD_CONFIG_ID_ATTR" value=""/>
<stringAttribute key="org.eclipse.cdt.launch.WORKING_DIRECTORY" value="/home/dom/Desktop/Jetson_TK1/HARP/bin"/>
<booleanAttribute key="org.eclipse.cdt.launch.use_terminal" value="true"/>
<listAttribute key="org.eclipse.debug.core.MAPPED_RESOURCE_PATHS">
<listEntry value="/HARP"/>
</listAttribute>
<listAttribute key="org.eclipse.debug.core.MAPPED_RESOURCE_TYPES">
<listEntry value="4"/>
</listAttribute>
<stringAttribute key="org.eclipse.dsf.launch.MEMORY_BLOCKS" value="&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot; standalone=&quot;no&quot;?&gt;&#10;&lt;memoryBlockExpressionList context=&quot;reserved-for-future-use&quot;&gt;&#10;&lt;gdbmemoryBlockExpression address=&quot;21925808&quot; label=&quot;_strides&quot;/&gt;&#10;&lt;/memoryBlockExpressionList&gt;&#10;"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.DefaultEvent" value="true"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.HideUnresolvedSymbols" value="true"/>
<stringAttribute key="org.eclipse.linuxtools.internal.perf.attr.Kernel.Location" value=""/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.Kernel.SourceLineNumbers" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.ModuleSymbols" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.MultipleEvents" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.Multiplex" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.Record.Realtime" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.Record.Verbose" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.ShowSourceDisassembly" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.ShowStat" value="false"/>
<booleanAttribute key="org.eclipse.linuxtools.internal.perf.attr.SourceLineNumbers" value="true"/>
<intAttribute key="org.eclipse.linuxtools.internal.perf.attr.StatRunCount" value="1"/>
<stringAttribute key="process_factory_id" value="org.eclipse.cdt.dsf.gdb.GdbProcessFactory"/>
</launchConfiguration>
"""
    
#==========================================
if __name__ == '__main__':
#==========================================    
#     Generator = EclipseGenerator()
#     Generator.run()
    pass



