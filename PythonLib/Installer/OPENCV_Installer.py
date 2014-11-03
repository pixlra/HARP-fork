#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from Base_Installer import *


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class OPENCV_Installer(Base_Installer):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
   
    #==========================================
    def __init__(self, Revision, BuildType, InfoStr, BaseDir ):
    #==========================================
        
        super(OPENCV_Installer, self).__init__(Revision, BuildType, InfoStr, BaseDir )
        
        # CHANGE HERE ------------------------------------------------------------------------------
        self.Name = "OPENCV"
        
        #self.CurRevision = "2.4.9"
        #self.Link = "http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.9/opencv-2.4.9.zip"
    
        self.CurRevision = "3.0.0"
        self.Link = "https://github.com/Itseez/opencv/archive/3.0.0-alpha.zip"
        
        self.RequiredTools = ("cmake",)
        
        assert(BuildType == "Release") #TODO
        #-------------------------------------------------------------------------------------------
        
        # GENERAL INIT
        assertToolsExist(self.RequiredTools)
        assert(self.Revision == Revision), "Error: Revision missmatch"
        self.BaseDir = res(BaseDir)
        self.BuildType = BuildType
        self.InfoStr = InfoStr 
        # END: GENERAL INIT
            
    #==========================================
    def build(self):
    #==========================================
            
        #setup BuildDir
        copyDir(self.SrcDir, self.BuildDir)
        #setup CMakeBuildDir and change into it
        createDir(self.CMakeBuildDir)
        os.chdir(self.CMakeBuildDir)
        
        # CHANGE HERE ------------------------------------------------------------------------------
        PythonArg = " -D BUILD_opencv_python2=ON " if self.Revision == "3.0.0" else " -D BUILD_opencv_python=ON "
        PrefixArg = " -D CMAKE_INSTALL_PREFIX=%s" % self.InstDir
        
        Cmd1 = ("cmake -D CMAKE_BUILD_TYPE=RELEASE "
               " -D WITH_OPENCL=OFF -D WITH_OPENCLAMDFFT=OFF -D WITH_OPENCLAMDBLAS=OFF " 
               " -D BUILD_EXAMPLES=ON -D WITH_OPENCL=OFF -D WITH_QT=OFF -D WITH_OPENGL=OFF -D WITH_GSTREAMER=ON "
               " %s %s %s "% (PrefixArg, PythonArg, self.BuildDir) )
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
        
        # CHANGE HERE ------------------------------------------------------------------------------
    
        #-------------------------------------------------------------------------------------------
    
        Cmd = "make install" 
        print "Cmd: " + Cmd
        logText("--%s-- build: %s" % (self.Name, Cmd), self.LogFN)
        assert os.system(Cmd)==0, "install failed"
   
        
    #====================================================================================
    # SPECIAL
    #====================================================================================
     


