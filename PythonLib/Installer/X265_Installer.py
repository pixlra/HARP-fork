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

class X265_Installer(Base_Installer):
    
    #==========================================
    def __init__(self, Revision, BuildType, InfoStr, BaseDir ):
    #==========================================
    
        super(X265_Installer, self).__init__(Revision, BuildType, InfoStr, BaseDir )
    
        # CHANGE HERE ------------------------------------------------------------------------------
        self.Name = "X265"

        self.CurRevision = "Tip"
        self.Link = "https://bitbucket.org/multicoreware/x265/get/tip.zip"
        
        self.RequiredTools = ("yasm", "cmake")
        
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
        
#     #==========================================
#     def download(self): #HG
#     #==========================================
#         if not os.path.exists(self.SrcDir):
#             Cmd = "hg clone https://bitbucket.org/multicoreware/x265 " + self.SrcDir
#             logText("--%s-- Download: %s" % (self.Name, Cmd), self.LogFN)
#             print "Cmd: " + Cmd
#             assert os.system(Cmd)==0, "download failed"
#         else:
#             print "Dir " + self.SrcDir + " exists, download skipped"
            

    #==========================================
    def build(self):
    #==========================================
        
        #setup BuildDir
        copyDir(self.SrcDir, self.BuildDir)
        #setup CMakeBuildDir and change into it
        createDir(self.CMakeBuildDir)
        os.chdir(self.CMakeBuildDir)
        
        # CHANGE HERE ------------------------------------------------------------------------------
        MakefileType = " -G \"Unix Makefiles\" "
        MakefileType = (" -G\"Eclipse CDT4 - Unix Makefiles\" " +
                        " -DCMAKE_BUILD_TYPE=%s " % self.BuildType +
                        " -DCMAKE_ECLIPSE_VERSION=%s " % self.HARP_Settings.get("Eclipse", "EclipseVersion")     +
                        " -DCMAKE_ECLIPSE_EXECUTABLE=%s " % self.HARP_Settings.get("Eclipse", "EclipseBin") )

        Cmd1 = "cmake " + MakefileType + " -DCMAKE_INSTALL_PREFIX=" + self.InstDir + " " + self.BuildDir + "/source"
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
        createDir(self.InstDir)
        os.chdir(self.CMakeBuildDir)
        
        #--------------------------------------
        # ENCODER CLASS SETUP
        #--------------------------------------
        EncBin = self.CMakeBuildDir + "/x265"
        INI_FN = ProjectDir + "/PythonLib/Encoder/X265_Settings.ini"   
        assert os.path.isfile(INI_FN), "INI file not found: " + INI_FN
        Sequ        = Sequence (ProjectDir + "/Various/Resources/Special/LMS_Logo_640x360.yuv", Fr=30, FPS=30)

        Encoder = X265_Encoder( OutputDir=ProjectDir + "/tmp", Passport="007", 
                                Name= self.Name, InfoStr="_Test", 
                                EncBin=EncBin, DecBin=None, INI_FN=INI_FN, OverrideStr="", 
                                Sequ=Sequ, QP=10,
                                PSNR_Tool=None)
        
        EncoderCmd = Encoder.get_CommandLineCall()
        print "EncoderCmd: " + EncoderCmd
        logText("--%s-- build: %s" % (self.Name, EncoderCmd), self.LogFN)
        
        #--------------------------------------
        # ECLIPSE PROJECT NAME PATCH
        #--------------------------------------
        EclProject = EclipseProject(self, Encoder)
        EclProject.setProjectName(self.DirName) #Name of directory gets Eclipse project name
        
        
        #--------------------------------------
        # ECLIPSE LAUNCH FILE GENERATION 
        #--------------------------------------
        EclProject.create_LaunchConfiguration(self.CMakeBuildDir)
        
        
        #--------------------------------------
        # MAKE INSTALL
        #-------------------------------------- 
        Cmd = "make install" 
        print "Cmd: " + Cmd
        logText("--%s-- build: %s" % (self.Name, Cmd), self.LogFN)
        assert os.system(Cmd)==0, "install failed"
   
        
    #====================================================================================
    # SPECIAL
    #====================================================================================
     
    #==========================================
    def createCallgrindScript(self, EncBin, EncArgs):
    #==========================================  
        Outfile = self.BuildDir + "/tmp/a_runCallgrind_Encoder.sh"
        with open(Outfile, 'w') as f:
            f.write(r'#!/bin/bash' + "\n\n")
            f.write("# Add --instr-atstart=no if necessary\n")
            f.write("valgrind --tool=callgrind --callgrind-out-file=Callgrind.out ")
            f.write("../" + EncBin + " " + EncArgs)
            os.chmod(Outfile, stat.S_IRWXU | stat.S_IRWXG);
            print "Callgrind script generated"

