#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from Base_Encoder import *
from Sequence import *



# HM_ENCODER: The TOOLBOX for the MATHEMATIKER
# HM_ENCODER: Either instantiated by INSTALLER or RATECURVE-CALCULATOR 

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class HM_Encoder(Base_Encoder):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self,  OutputDir, Passport, 
                        Name, InfoStr, 
                        EncBin, DecBin, INI_FN, OverrideStr, 
                        Sequ, QP,
                        PSNR_Tool):
    #==========================================
    
        super(HM_Encoder, self).__init__(
                        OutputDir, Passport, 
                        Name, InfoStr, 
                        EncBin, DecBin, INI_FN, OverrideStr, 
                        Sequ, QP,
                        PSNR_Tool)
    
    #==========================================
    def get_CommandLineCall(self):
    #==========================================
        Call = "\"" +self.EncBin + "\"" + self.get_CommandLineArguments()
        return Call
        
    #==========================================   
    def get_CommandLineArguments(self):
    #==========================================

        # first, read some specific values from INI
        self.bitstream = self.OutputDir + "/" + self.Passport + "_str.bin"
        self.recyuv    = self.OutputDir + "/" + self.Passport + "_rec.yuv"
        
        # setting input file
        Args = " --InputFile=\"" + self.Sequ.AbsFN + "\""
                
        # special: HM config file (state first so that it can be overriden)
        HM_CfgFile = ProjectDir + "/Src_HM/cfg/" + self.Config.get("General", "CfgFile")
        assertFileExists(HM_CfgFile, "HM Config File not found")
        Args += " -c %s " % HM_CfgFile
        
        # setting stuff which is not in INI
        Args += " --BitstreamFile=%s"  % self.bitstream
        Args += " --SourceWidth=%d"  % self.Sequ.DimX
        Args += " --SourceHeight=%d" % self.Sequ.DimY
        Args += " --FramesToBeEncoded=%d" % self.Sequ.Fr
        Args += " --ReconFile=%s"  % self.recyuv
        Args += " --FrameRate=%d"  % self.Sequ.FPS
        
        # setting ini arguments
        Args += self.get_INI_Arguments()
        
        # setting QP
        Args += " --QP=%d" % self.QP
                
        return Args
        
#==========================================
if __name__ == '__main__':
#==========================================  

    printLARGE("TESTING HM_ENCODER")

    TmpDir   = "/home/dom/Desktop/Jetson_TK1/HARP/tmp/"
    Passport = "007" 
    
    Name     = "HM"
    InfoStr  = "_Test"
    
    EncBin = "/home/dom/Desktop/Jetson_TK1/HARP/bin/TAppEncoder"
    DecBin = None
    INI_FN = "/home/dom/Desktop/Jetson_TK1/HARP/PythonLib/Encoder/HM_Encoder.ini"   
    OverrideStr = ""
    
    Sequ        = Sequence("GT/Kingsport_roll_640x360.yuv", Fr=30, FPS=30)
    QP          = 10
    
    PSNR_Tool   = None
    
    Encoder = HM_Encoder( TmpDir, Passport, 
                            Name, InfoStr, 
                            EncBin, DecBin, INI_FN, OverrideStr, 
                            Sequ, QP,
                            PSNR_Tool)
    
    print "Created HM command:"
    print Encoder.get_CommandLineCall()
    
    
