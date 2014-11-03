#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

#====================================================================================
# YASM
#====================================================================================

class CLib_YASM():

    Name = "YASM"
    Revision = "1.2"
    
    #==========================================
    def __init__(self, Revision, BuildType, InfoStr, BaseDir ):
    #==========================================
        
        assert(self.Revision == Revision), "Error: Revision missmatch"
        self.BaseDir = res(BaseDir)
        self.BuildType = BuildType
        self.InfoStr = InfoStr 
        self.ScriptDir = os.path.dirname(os.path.abspath(__file__)) # location of script
        
    #==========================================
    def download(self):
    #==========================================
        if not os.path.exists(self.SrcDir):
            Cmd = "curl -L -o /tmp/yasm.tar.gz http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz"
            print "Cmd: " + Cmd
            assert os.system(Cmd)==0, "download failed"
            os.chdir("/tmp")    # tar crap
            Cmd = "tar xfz /tmp/yasm.tar.gz" 
            assert os.system(Cmd)==0, "decompress failed" 
            shutil.copytree("/tmp/yasm-1.2.0", self.SrcDir) #find out by "extract here"
            os.chdir(self.BaseDir) #back to working directory
        else:
            print "Dir " + self.SrcDir + " exists, download skipped"
            
    #==========================================
    def build(self):
    #==========================================        
        shutil.copytree(self.SrcDir, self.BuildDir)
        os.chdir(self.BuildDir)

        Cmd1 = "./configure --prefix=" + self.InstDir
        Cmd2 = "make -j 4"

        print "Cmd1: " + Cmd1
        print "Cmd2: " + Cmd2
        
        assert os.system(Cmd1)==0, "configure failed"
        assert os.system(Cmd2)==0, "make failed"
        
    #==========================================
    def install(self):
    #==========================================
        Cmd = "make install" 
        print "Cmd1: " + Cmd
        assert os.system(Cmd)==0, "install failed"
   
        
    #====================================================================================
    # SPECIAL
    #====================================================================================
     


