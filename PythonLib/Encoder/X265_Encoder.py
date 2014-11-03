#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from Base_Encoder import *
from Sequence import *



# X265_ENCODER: The TOOLBOX for the MATHEMATIKER
# X265_ENCODER: Either instantiated by INSTALLER or RATECURVE-CALCULATOR 

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class X265_Encoder(Base_Encoder):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self,  OutputDir, Passport, 
                        Name, InfoStr, 
                        EncBin, DecBin, INI_FN, OverrideStr, 
                        Sequ, QP,
                        PSNR_Tool):
    #==========================================
    
        super(X265_Encoder, self).__init__(
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
        self.bitstream = self.OutputDir + "/" + self.Passport + "_str.h265"
        self.recyuv    = self.OutputDir + "/" + self.Passport + "_rec.yuv"
        
        # setting input file
        Args = " --input=\"" + self.Sequ.AbsFN + "\""
        
        # setting stuff which is not in INI
        Args += " --output="  + self.bitstream
        Args += " --input-res=%dx%d" % (self.Sequ.DimX, self.Sequ.DimY) 
        Args += " --frames=%d" % self.Sequ.Fr
        Args += " --fps=%d"    % self.Sequ.FPS
        Args += " --recon=%s"  % self.recyuv
        
        # setting ini arguments
        Args += self.get_INI_Arguments()
        
        # setting QP
        Args += " --qp=%d" % self.QP
                
        return Args
        
#==========================================
if __name__ == '__main__':
#==========================================  

    printLARGE("TESTING X265_ENCODER")

    TmpDir   = "/home/dom/Desktop/Jetson_TK1/HARP/tmp/"
    Passport = "007" 
    
    Name     = "x265"
    InfoStr  = "_Test"
    
    EncBin = "/home/dom/Desktop/X265_Sep30_4/build/linux/x265"
    DecBin = None
    INI_FN = "/home/dom/Desktop/Jetson_TK1/HARP/PythonLib/Encoder/X265_Settings.ini"   
    OverrideStr = ""
    
    Sequ        = Sequence("GT/Kingsport_roll_640x360.yuv", Fr=30, FPS=30)
    QP          = 10
    
    PSNR_Tool   = None
    
    Encoder = X265_Encoder( TmpDir, Passport, 
                            Name, InfoStr, 
                            EncBin, DecBin, INI_FN, OverrideStr, 
                            Sequ, QP,
                            PSNR_Tool)
    
    print "Created X265 command:"
    print Encoder.get_CommandLineCall()
    
    
