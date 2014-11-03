#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
import zipfile
import tarfile


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class Base_Installer(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self, Revision, BuildType, InfoStr, BaseDir ):
    #==========================================
        self.BaseDir = res(BaseDir)
        self.BuildType = BuildType
        self.InfoStr = InfoStr 
        self.Revision = Revision
        self.LogFN = ProjectDir + "/tmp/Log.txt"
        
    #==========================================
    def finalsetup(self, Main):
    #==========================================
    
        self.DirName = self.Name + ("d" if self.BuildType == "Debug" else "") + "_" + self.Revision + self.InfoStr
        print "Directory: " + self.DirName 
    
        #--------------------------------------
        # LOCATIONS OF THIS LIBRARY
        #--------------------------------------  
        self.SrcDir          = getAbsPath( self.BaseDir +  "/z_src/"   + self.DirName            ) # will not download again if this exists
        self.BuildDir        = getAbsPath( self.BaseDir +  "/z_build/" + self.DirName            ) # allow out-of-source build even for non-CMakes
        self.CMakeBuildDir   = getAbsPath( self.BaseDir +  "/z_build/" + self.DirName + "_BUILD" ) # dedicated CMake build dir, on same level (->Eclipse Generator) 
        self.InstDir         = getAbsPath( self.BaseDir +  "/"         + self.DirName            ) # installation dir
        
        if Main.DeveloperVersion:
            self.SrcDir          = "/tmp/src_"             + self.DirName
            self.BuildDir        = self.BaseDir +  "/"     + self.DirName
            self.CMakeBuildDir   = self.BaseDir +  "/"     + self.DirName + "_BUILD"
            self.InstDir         = "/tmp/inst_"            + self.DirName
           
        print "--------------------------"
        print "Installing:"
        print "--------------------------"
        print "Name:      " + self.Name
        print "Revision:  " + self.Revision
        print "BuildType: " + self.BuildType
        print "InfoStr: "   + self.InfoStr
        print "Using YASM  under: %s" % Main.YasmDir
        print "Using CMAKE under: %s" % Main.CMakeDir
        print "--------------------------"
        print "Current dir: "   + os.getcwd()
        print "BaseDir: "       + self.BaseDir
        print "SrcDir:  "       + self.SrcDir
        print "BuildDir: "      + self.BuildDir
        print "CMakeBuildDir: " + self.CMakeBuildDir
        print "Install dir: "   + self.InstDir  
        print "--------------------------"
    
        assert " " not in self.BaseDir, "Basedir contains spaces"
        assertToolsExist(self.RequiredTools)
        assert(self.CurRevision == self.Revision), "Error: Revision mismatch"
        
        #--------------------------------------
        # CLEAN DIRS
        #--------------------------------------         
        
        os.system("mkdir -p " + self.BaseDir) #just making sure
        os.chdir(self.BaseDir) 
        
        #--------------------------------------
        # CLEAN DIRS
        #-------------------------------------- 
        if Main.allowDelete:
            assert self.Name in self.BuildDir       # last line of defence
            assert self.Name in self.CMakeBuildDir  # last line of defence
            deleteDir(self.BuildDir)
            deleteDir(self.CMakeBuildDir)
        if not Main.allowOverwrite:   
            assert not os.path.exists(self.BuildDir), "Dir %s exists, are you sure? Exiting." % self.BuildDir   
    

    #==========================================
    def download(self): #ZIP
    #==========================================
    
        dummy, LinkType = os.path.splitext(self.Link)
        #--------------------------------------
        if LinkType == ".zip":
        #--------------------------------------
            if not os.path.exists(self.SrcDir):
                Cmd = "wget -O /tmp/downloaded.zip " + self.Link
                print "Cmd: " + Cmd
                if not os.system(Cmd)==0:
                    print "WARNING: wget download failed, trying curl"
                    Cmd = "curl -L -o /tmp/downloaded.zip " + self.Link
                    print "Cmd: " + Cmd
                    assert(os.system(Cmd)==0), "curl download failed"
                zip=zipfile.ZipFile('/tmp/downloaded.zip')
                #ZipDirs = [x for x in zip.namelist() if x.endswith('/')]
                ZipDirs = zip.namelist()
                Dir, FN = os.path.split(ZipDirs[0])
                DirComponents = Dir.split(os.sep)#
                assert(len(DirComponents) == 1)
                TopLevelDir = DirComponents[0]
                #if not ZipDirs: #list empty, 
                    
                os.chdir("/tmp") # temporary untar 
                Cmd = "unzip -o /tmp/downloaded.zip -d /tmp/downloaded" #-o force overwrite
                assert os.system(Cmd)==0, "decompress failed" 
                shutil.copytree("/tmp/downloaded/" + TopLevelDir, self.SrcDir)
                os.chdir(self.BaseDir) #back to working directory
            else:
                print "Dir " + self.SrcDir + " exists, download skipped"
        #--------------------------------------        
        elif LinkType == ".gz":  # TAR.GZ
        #--------------------------------------
            if not os.path.exists(self.SrcDir):
                Cmd = "wget -O /tmp/downloaded.tar.gz " + self.Link
                print "Cmd: " + Cmd
                if not os.system(Cmd)==0:
                    print "WARNING: wget download failed, trying curl"
                    Cmd = "curl -L -o /tmp/downloaded.tar.gz " + self.Link
                    print "Cmd: " + Cmd
                    assert(os.system(Cmd)==0), "curl download failed"  
                tar = tarfile.open("/tmp/downloaded.tar.gz") 
                TarInfos = tar.getmembers()
                TarInfo = TarInfos[0]
                assert(TarInfo.isdir())
                TopLevelDir = TarInfo.name
                
                os.chdir("/tmp") # temporary untar
                Cmd = "tar xfz /tmp/downloaded.tar.gz" 
                assert os.system(Cmd)==0, "decompress failed" 
                shutil.copytree("/tmp/" + TopLevelDir, self.SrcDir)
                os.chdir(self.BaseDir) #back to working directory
            else:
                print "Dir " + self.SrcDir + " exists, download skipped"     
        else: # LinkType not yet supported
            assert(0)
