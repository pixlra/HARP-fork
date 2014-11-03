#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from Sequence import *
from Encoder.X265_Encoder import *
from Installer.EclipseProject import *
from Base_Installer import *


#====================================================================================
# X265
#====================================================================================

class YASM_Installer(Base_Installer):
    
    #==========================================
    def __init__(self, Revision, BuildType, InfoStr, BaseDir ):
    #==========================================
    
        super(YASM_Installer, self).__init__(Revision, BuildType, InfoStr, BaseDir )
    
        # CHANGE HERE ------------------------------------------------------------------------------
        self.Name = "YASM"

        self.CurRevision = "1.2"
        self.Link = "http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz"
        
        self.RequiredTools = ()
        
        assert(BuildType == "Release") #TODO
        #-------------------------------------------------------------------------------------------
       
        # GENERAL INIT
        assertToolsExist(self.RequiredTools)
        assert(self.Revision == Revision), "Error: Revision missmatch"
        self.BaseDir = res(BaseDir)
        self.BuildType = BuildType
        self.InfoStr = InfoStr 
        # END: GENERAL INIT

        self.HARP_Settings = load_INI(ProjectDir + "/HARP_Settings.ini");
     
    #==========================================
    def setup(self, DirName, SrcDir, BuildDir, CMakeBuildDir, InstDir):
    #==========================================   
        self.DirName        = DirName
        self.SrcDir         = SrcDir
        self.BuildDir       = BuildDir
        self.CMakeBuildDir  = CMakeBuildDir
        self.InstDir        = InstDir

    #==========================================
    def build(self):
    #==========================================
        
        #setup BuildDir
        copyDir(self.SrcDir, self.BuildDir)
        #setup CMakeBuildDir and change into it
        #createDir(self.CMakeBuildDir)
        #os.chdir(self.CMakeBuildDir)
        os.chdir(self.BuildDir)
        
        
        # CHANGE HERE ------------------------------------------------------------------------------
        Cmd1 = "./configure --prefix=" + self.InstDir
        Cmd2 = "make -j 4"
        #-------------------------------------------------------------------------------------------
        
        logText("--%s-- build: %s" % (self.Name, Cmd1), self.LogFN)
        logText("--%s-- build: %s" % (self.Name, Cmd2), self.LogFN)
        print "Cmd1: " + Cmd1
        print "Cmd2: " + Cmd2        
        assert os.system(Cmd1)==0, "cmake failed"
        assert os.system(Cmd2)==0, "make failed"
        
    #==========================================
    def install(self):
    #==========================================
        
        #--------------------------------------
        # MAKE INSTALL
        #-------------------------------------- 
        Cmd = "make install" 
        print "Cmd: " + Cmd
        logText("--%s-- build: %s" % (self.Name, Cmd), self.LogFN)
        assert os.system(Cmd)==0, "install failed"
   
        


