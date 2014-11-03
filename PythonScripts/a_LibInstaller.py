#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import sys, os
__builtins__.ProjectDir = os.path.abspath("../")
__builtins__.LibDir = ProjectDir + "/PythonLib"
__builtins__.TmpDir = ProjectDir + "/tmp"
sys.path.append(LibDir) 

from Imports_Basic import *

#from CLib_YASM import *
#from CLib_LIBYUV import *
#from CLib_OPENCV import *
#from CLib_CMAKE import *
from Installer.X265_Installer import *
from Installer.OPENCV_Installer import *
from Installer.YASM_Installer import *

# from CLib_HM import *
# from CLib_VP9 import *
# from CLib_LIBYUV import *
# from CLib_X264 import *
# from CLib_LIBAV import *
# from CLib_GST import *

# GENERAL ==============================
# InfoStr: e.g. "_VisualizerOn", appended to DirectoryName, just to make a certain (test) installation unique 
# Requirements: git, git-svn, svn, mercurial, cmake, python-devel, numpy, matplotlib, matplotlib-tk, curl
# Info(prepend "_" to InfoStr)
#==========================================


# CONVENTIONS ==============================
# WARNING: changing these conventions will most likely BREAK EVERYTHING. 
# ALLOWS: ready-to-use environment on any Ubuntu/Suse/CentOS (virtual) system, essential for future WINDOWS ports
# Convention A: directly under HOME: "lib" for std libs, "lib_Codecs" for special libs (like Std HM)
# Convention B: "z_src" holds downloaded sources, which are then copied to "z_build" for compilation
# Convention C: each lib is installed after compilation, directly into the lib/lib_Codecs directory  
# Example:
# ~
# ├── lib
# │   ├── OPENCV_2.4.9
# │   ├── YASM_1.2
# │   ├── z_build
# │   └── z_src
# ├── lib_Codecs
# │   ├── HM_13.0_Std
# │   ├── z_build
# │   └── z_src
#==========================================


# TODO ====================================
# YASM and CMAKE version check and auto-installation
# Test for existence of all required tools
# adapt VP9 patches so that it finds and links our OWN OpenCV 
# TODO: pass over number of cores for compilation
# TODO: safety checks individually for each library (e.g.: hg may only be required by a subset)
# TODO: eventuell tar.gz Downloads besser geeignet als HG
#==========================================

class CMain():

    #==========================================
    def __init__(self):
    #==========================================
        #forceRunInScreen()
        assertToolsExist( ("git", "git svn", "hg", "curl", "unzip", "wget") )
                         
        # CHANGE HERE ------------------------------------------------------------------------------
        
        # ENVIRONMENT
        self.YasmDir = res("~/lib/YASM_1.2") #set manually, other libs may need this
        self.CMakeDir = res("~/lib/CMAKE_2.8") #set manually, other libs may need this
        os.environ["PATH"] = self.YasmDir + "/bin:" + os.environ["PATH"]
        os.environ["PATH"] = self.CMakeDir + "/bin:" + os.environ["PATH"]        
        
        # SETTINGS
        self.DeveloperVersion = False  #Special install: download+compile under /tmp (for fast tests, set BaseDir="~/Desktop/TESTABC")

        #self.X264Dir = res("~/lib_Codecs/X264_May30") #set manually, for libav
        self.allowDelete    = False # use at own risk! Allows deletion of build directories for clean build
        self.allowOverwrite = False # use at own risk! Allows existing directories to be overwritten
        
        # BASIC LIBS 
        #self.LibList.append(  CLib_YASM   ("1.2",   "Release", InfoStr="", BaseDir="~/lib"))
        #self.LibList.append(  CLib_CMAKE ("2.8", "Release", InfoStr="", BaseDir="~/lib"))
        #self.LibList.append(  CLib_LIBYUV ("Nov13", "Release", InfoStr="", BaseDir="~/lib"))
        #self.LibList.append(  CLib_OPENCV ("2.4.9", "Release", InfoStr="", BaseDir="~/lib"))
        #self.run( OPENCV_Installer("3.0.0", "Release", InfoStr="", BaseDir="~/lib"))
        
        # CODECS
        self.run(  YASM_Installer   ("1.2",   "Release", InfoStr="", BaseDir="~/lib"))
        #self.run(  X265_Installer   ("Sep30",  "Release", InfoStr="_1", BaseDir="~/Desktop"))
        self.run(  X265_Installer   ("Tip",  "Release", InfoStr="", BaseDir="~/lib_Codecs"))
        
        #--------------------------------------------------------------------------------------------
        

        
        #assert ("2.8" in CMakeVersion), "CMake version not 2.8, but: " + CMakeVersion
        #assertDirExists(self.YasmDir,   "YASM directory not found")
        #assertDirExists(self.CMakeDir, "CMAKE directory not found")

        
    #==========================================
    def run(self, Installer):
    #==========================================
        
        #--------------------------------------
        # SETTING YASM PATH
        #-------------------------------------- 
#             if "YASM" not in Lib.Name: # exclude case: compilation of yasm itself
#                 assertDirExists(self.YasmDir, "YASM directory not found")
#                 os.environ["PATH"] = self.YasmDir + "/bin:" + os.environ["PATH"]
        
        #--------------------------------------
        # DO YA THANG
        #--------------------------------------  
        if 1: # DEBUG
            self.allowDelete = True
            Installer.finalsetup(self) #do not uncomment this
            Installer.download()
            Installer.build() # debug notice: dont forget to disable clean dirs
            Installer.install()
        else:
            Installer.finalsetup(self) 
            Installer.download()
            Installer.build()  
            Installer.install()
        
        print "\n" + Installer.Name + ": DONE"
        print ">>>>------------------------------\n"
                
 

#==========================================
if __name__ == '__main__':
#==========================================
    #sys.exit(0)
    
    Main = CMain()
    #Main.run() # constructor does the magic
