#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class Base_Encoder(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #Name     = None
    #EncBin   = None
    #DecBin   = res("~/lib_Codecs/HM_13.0_Std/bin/TAppDecoder")
    #Ini      = self.get_INI_Content(SrcDir + "/HM_Encoder.ini")
    #PSNR     = PSNRTool
    #Override = "ReservedForOverride"
    #InfoStr  = "ReservedForInfoString"

    #==========================================
    def __init__(self, OutputDir, Passport, 
                        Name, InfoStr, 
                        EncBin, DecBin, INI_FN, OverrideStr, 
                        Sequ, QP,
                        PSNR_Tool):
    #==========================================
        #self.ScriptDir = os.path.dirname(os.path.abspath(__file__)) # location of script
        #self.TmpDir = os.path.abspath(self.ScriptDir + "/../../tmp")
    
        self.OutputDir     = OutputDir
        self.Passport   = Passport
    
        self.Name       = Name
        self.InfoStr     = InfoStr
        
        self.EncBin     = EncBin
        self.DecBin     = DecBin
        self.INI_FN     = INI_FN
        self.OverrideStr = OverrideStr
        
        self.Sequ       = Sequ
        self.QP         = QP
    
        self.PSNR_Tool  = PSNR_Tool
                
        self.Config = load_INI(INI_FN);
        self.Prefix = os.path.expandvars(self.Config.get("General", "Prefix")) #expand $HOME
    
        assertFileExists(EncBin, "EncBin missing")
        #assertFileExists(DecBin, "DecBin missing")
        assertFileExists(INI_FN, "INI_FN missing")
        assertFileExists(Sequ.AbsFN, "Sequ.AbsFN missing")
        #assertFileExists(PSNR_Tool, "PSNR_Tool missing")
        
    
    #==========================================
    def set_Sequence(Sequ):
    #==========================================  
        self.Sequ = Sequ
        
    #==========================================
    def set_QP(QP):
    #==========================================  
        self.QP = QP
        
    #==========================================
    def printEncoderInfo(self):
    #==========================================
        assert Sequ != None and QP != None
       
        print "\n----------------------------------"
        print self.Name + "-Encoding of " + basename(self.Sequ.BN)
        print "QP = " + self.QP
        print "----------------------------------"
        print "Encoder: using enc binary " + self.Codec.EncBin
        print "Encoder: using dec binary " + self.Codec.DecBin
        print "Encoder: OverrideStr " + (self.OverrideStr if self.OverrideStr != "" else "off")
        print "Encoder: ParamName  = " + self.ParamName 
        print "Encoder: ParamValue = " + str(self.ParamValue) 
        
    #==========================================
    def get_INI_Arguments(self):
    #==========================================
        Call = ""
    
        # Section
        Section = "Args_Sequence"
        List = self.Config.options(Section)
        for Arg in List:
            Value = self.Config.get(Section, Arg)
            if Value != None: #if no value present
                Final = (" %s%s=%s" %(self.Prefix, Arg, Value))
            else:
                Final = (" %s%s" %(self.Prefix, Arg))
            Call += Final
            
        # Section 
        Section = "Args_RDO"
        List = self.Config.options(Section)
        for Arg in List:
            Value = self.Config.get(Section, Arg)
            if Value != None: #if no value present
                Final = (" %s%s=%s" %(self.Prefix, Arg, Value))
            else:
                Final = (" %s%s" %(self.Prefix, Arg))
            Call += Final
            
        # Section 
        Section = "Args_Encoding"
        List = self.Config.options(Section)
        #print List
        for Arg in List:
            Value = self.Config.get(Section, Arg)
            if Value != None: #if no value present
                Final = (" %s%s=%s" %(self.Prefix, Arg, Value))
            else:
                Final = (" %s%s" %(self.Prefix, Arg))
            Call += Final
            
        # Section 
        Section = "Args_Other"
        List = self.Config.options(Section)
        for Arg in List:
            Value = self.Config.get(Section, Arg)
            if Value != None: #if no value present
                Final = (" %s%s=%s" %(self.Prefix, Arg, Value))
            else:
                Final = (" %s%s" %(self.Prefix, Arg))
            Call += Final
            
            
        # setting override argument
        if self.OverrideStr != "":
            print "Overriding with: " + self.OverrideStr
            Call += " " + self.OverrideStr
            
        return Call
    
    #==========================================
    def calculate_PSNR_SSIM(self, recyuv):
    #==========================================

        #PSNR
        Call = self.Codec.PSNR + " -psnr -s " + self.DimX + " " + self.DimY + " " + recyuv + " \"" + self.SequName + "\""
        process = subprocess.Popen(Call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        out, err = process.communicate()
        print "PSNR tool returned:\n" + out
        assert(process.returncode == 0)
        
        #REGEX SEARCH
        res1 = re.search(r"Avg:\s*\d*\.\d*\t", out)
        assert res1 != None, "Regex not found"
        res2 = re.search(r"\d*\.\d*", res1.group())
        assert res2 != None, "Regex not found"
        result = float(res2.group())
        PSNR = result
        
        #SSIM
        Call = self.Codec.PSNR + " -ssim -s " + self.DimX + " " + self.DimY + " " + recyuv + " \"" + self.SequName + "\""
        process = subprocess.Popen(Call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        out, err = process.communicate()
        assert(process.returncode == 0)
        print "SSIM tool returned:\n" + out
        
        #REGEX SEARCH
        res1 = re.search(r"Avg:\s*\d*\.\d*\t", out)
        assert res1 != None, "Regex not found"
        res2 = re.search(r"\d*\.\d*", res1.group())
        assert res2 != None, "Regex not found"
        result = float(res2.group())
        SSIM = result
            
        print "Avg Y-PSNR: " + str(PSNR)
        print "Avg Y-SSIM: " + str(SSIM)
        return PSNR, SSIM
    
    #==========================================
    def calculateResults(self, recyuv):
    #==========================================
        PSNR, SSIM = self.calculate_PSNR_SSIM(recyuv)
        
        # calculating bitrate
        FilesizeBytes = float(os.path.getsize(self.bitstream))
        BitrateMBits = (FilesizeBytes * 8 * float(self.Fps)) / (float(self.NumFrames) * 1000 * 1000)
        print("Size of %s: %.4f KB" % (self.bitstream, FilesizeBytes/1000))
        print("Bitrate: %.8f MBit/s" % BitrateMBits)
        
        #str(self.ParamValue) + "\t\t" + 
        Result = str(self.ParamValue) + "\t\t" + \
                 "{:.4f}".format(PSNR) + "\t\t" + "{:.4f}".format(SSIM) + \
                 "\t\t" + "{:.4f}".format(BitrateMBits) + "\n"
        
        return Result
    
    #==========================================
    def appendToLog(self, Call, out, err):
    #==========================================
        #we keep this call for later
        self.ThreadLock.acquire() 
        LogFileName = "./tmp/Log_" + self.Codec.Name + "_CalledCommands.txt"
        Log = open(LogFileName, "a")
        Log.write(Call + "\n\n")
        Log.close()
        
        LogFileName = "./tmp/Log_" + self.Codec.Name + "_Stdout.txt"
        Log = open(LogFileName, "a")
        Log.write("=========================================\n")
        Log.write("Call:\n" + Call + "\n")
        Log.write("=========================================\n")
        Log.write("Stdout:\n" + out + "\nStderr:\n" + err + "\n\n\n")
        Log.close()
        self.ThreadLock.release()  
    

    #==========================================
    def execute(self, Call):
    #==========================================
    

        print "Calling (one liner): "
        print Call
        print "Calling (human readable): " 
        print Call.replace(" ", "\n")
        
        # Calling!
        #assert os.system(Call) == 0, "Encoder call returned error" 
        
        process = subprocess.Popen(Call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        
        # activate real-time output on stdout
        for line in iter(process.stdout.readline, b''):
            print line,
        
        out, err = process.communicate()
        self.appendToLog(Call, out, err)
        
        ErrorStr = "Error: Call returned -1\n" + Call + "\nStdout:\n" + out + "\nStderr:\n" + err
        assert(process.returncode == 0), ErrorStr
        #print "Stdout:\n" + out + "\nStderr:\n" + err
        

