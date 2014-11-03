#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

import stat

#====================================================================================
# LIBYUV
#====================================================================================

class CLib_LIBYUV():

    Name = "LIBYUV"
    Revision = "Nov13"
    
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
            Cmd = "git svn clone -r 844 http://libyuv.googlecode.com/svn/trunk/ " + self.SrcDir
            print "Cmd: " + Cmd
            if os.system(Cmd) != 0: #try svn, maybe git-svn is missing
                print color.WARNING + "Warning: git-svn seems to be missing" + color.END
                Cmd = "svn checkout http://libyuv.googlecode.com/svn/trunk/@844 " + self.SrcDir
                print "Cmd: " + Cmd
                assert os.system(Cmd)==0, "download failed"
        else:
            print "DOWNLOAD SKIPPED! Dir " + self.SrcDir + " already exists"
            
    #==========================================
    def build(self):
    #==========================================
        shutil.copytree(self.SrcDir, self.BuildDir)
        os.chdir(self.BuildDir + "/util")
        
        
        for line in fileinput.input("./Makefile", inplace=1, backup='.bak'):
            line = re.sub('-static',' ', line.rstrip()) # FIX FOR SUSE (STATIC LIBRARIES NOT FOUND)
            line = re.sub('-msse2',' ', line.rstrip())  # FIX FOR PANDABOARD
            print(line)
        
        if self.BuildType == "Release":
            Cmd = "make"
        else:
            Cmd = "make"
        print "Cmd: " + Cmd
        assert os.system(Cmd)==0, "make failed"
        
    #==========================================
    def install(self):
    #==========================================
        os.system("mkdir -p " + self.InstDir + "/bin") 
        shutil.copy(self.BuildDir + "/util/psnr", self.InstDir + "/bin/")
   
        
    #====================================================================================
    # SPECIAL
    #====================================================================================
     


