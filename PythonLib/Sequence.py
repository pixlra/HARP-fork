#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

from OpenCV import *

# import os.path
# from os.path import basename
# import sys
# import numpy as np
# import shutil
# import copy
# import Image

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class Sequence:
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    
    #==========================================
    def __init__(self, SequName, Fr, FPS):
    #==========================================
        if SequName.startswith("/"): #absolute path
            AbsFN = SequName
        else:
            SequenceDir = res("~/Sequenzen") #the usual suspects
            AbsFN = SequenceDir + "/" + SequName    
    
        assert os.path.isfile(AbsFN), "YUV file not found: " + AbsFN    
        (self.FN, self.BN, self.Dir, self.DIRBN, self.AbsFN) = splitPathFN(AbsFN)
        self.Name = self.BN
        (self.DimX, self.DimY) = get_DimX_DimY_from_Filename(self.FN)
        (self.Fr, self.FPS, self.FrameSize) = (Fr, FPS, self.DimX*self.DimY*1.5)
        
        self.FH = open(AbsFN, "rb")
        self.FH.seek(0, os.SEEK_END)
        self.NumBytes = self.FH.tell()
        self.FH.seek(0, os.SEEK_SET)
        self.FrameSize = (self.DimX*self.DimY*1.5)
        TotalNumFr = int(self.NumBytes/self.FrameSize)
        if self.Fr > TotalNumFr: # if we ask for more than we can get
            self.Fr = TotalNumFr
    
    #==========================================
    def getPOC_Y(self, POC):
    #==========================================    
        last_pos = self.FH.tell() 
        self.FH.seek(POC*self.FrameSize, os.SEEK_SET)
        
        Raw = self.FH.read(self.DimX*self.DimY)
        Y = Image.frombuffer('L', (self.DimX,self.DimY), Raw, 'raw', 'L', 0, 1)
        Cb = self.FH.read(self.DimX*self.DimY/4)
        Cr = self.FH.read(self.DimX*self.DimY/4)
        Y = np.array(Y)
        
        self.FH.seek(last_pos, os.SEEK_SET)
        return Y
    
    #==========================================
    def getPOC(self, POC):
    #==========================================   
        last_pos = self.FH.tell() 
        self.FH.seek(POC*self.FrameSize, os.SEEK_SET)
    
        Y_Raw = self.FH.read(self.DimX*self.DimY)
        U_Raw = self.FH.read(self.DimX*self.DimY/4)
        V_Raw = self.FH.read(self.DimX*self.DimY/4)
        
        Y = np.array(Image.frombuffer('L', (self.DimX,self.DimY),     Y_Raw, 'raw', 'L', 0, 1) )
        U = np.array(Image.frombuffer('L', (self.DimX/2,self.DimY/2), U_Raw, 'raw', 'L', 0, 1) )
        V = np.array(Image.frombuffer('L', (self.DimX/2,self.DimY/2), V_Raw, 'raw', 'L', 0, 1) )
        
        U = cv2.resize(U, (self.DimX, self.DimY), interpolation=cv2.INTER_CUBIC)
        V = cv2.resize(V, (self.DimX, self.DimY), interpolation=cv2.INTER_CUBIC)
        
        self.FH.seek(last_pos, os.SEEK_SET)
        YUV = np.dstack((Y, U, V))
        return YUV   
    
    #==========================================
    def getGHT(self, POC):
    #==========================================  
        #TODO
        return None
    
    #==========================================
    def getSAD(self, POC):
    #==========================================
        RefY  = self.getPOC_Y(POC-1) 
        CurY  = self.getPOC_Y(POC) 
        SAD = np.sum(np.abs(np.int16(CurY) - np.int16(RefY))) / self.DimX / self.DimY 
        return SAD
     
    #==========================================
    def get_LA_GT(self):  # Groundtruth Labels
    #==========================================     
        INI = loadINI(self.DIRBN + ".ini" )
        RotatingPOCS_GT = [int(Entry) for Entry in INI.get("RotatingPOCS")]
        ZoomingPOCS_GT  = [int(Entry) for Entry in INI.get("ZoomingPOCS")]
        
        LA_GT = np.zeros(self.Fr, np.uint8)
        for POC in np.arange(self.Fr):
            if POC in RotatingPOCS_GT:
                LA_GT[POC] = ROT
            if POC in ZoomingPOCS_GT:
                LA_GT[POC] = ZOOM
        return LA_GT
    
    #==========================================
    def get_FE_GT(self):  # Groundtruth Features (e.g. angles, ratios)
    #==========================================     
        INI = loadINI(self.DIRBN + ".ini" )
        RotationAngles_GT = [float(Entry) for Entry in INI.get("RotationAngles")]
        EigenvalRatios_GT = [float(Entry) for Entry in INI.get("EigenvalRatios")]
        
        RotationAngles_GT=np.array(RotationAngles_GT)[:self.Fr]
        EigenvalRatios_GT=np.array(EigenvalRatios_GT)[:self.Fr]
        
#         FE_GT = np.zeros((self.Fr,2), np.float32)
#         FE_GT[:,0] = np.array(RotationAngles_GT)
#         FE_GT[:,1] = np.array(EigenvalRatios_GT)
        return (RotationAngles_GT, EigenvalRatios_GT)
    
    #==========================================
    def getMask(self):
    #==========================================
        FN = self.DIRBN + "_Mask.png"      
        #assert os.path.isfile(FN), "Mask file missing:" + FN
        
        if os.path.isfile(FN):
            GtMask = cv2.imread(FN, 0) 
            GtMask /= 255  
        else:
            warning("\n\n>>> WARNING: MASK NOT FOUND, SETTING TO NONE!!\n\n")
            #assert(0), "MASK NOT FOUND"
            GtMask = None
        
        return GtMask  
        
        #GtMask = np.zeros((self.DimY, self.DimX), np.uint8)


#==========================================
def write_YUV(FH, Cur):
#==========================================
#     for cnt in range(0,6):
#         self.writeText(Cur, (0,10+64*cnt), "%d" % POC)
    
    y,u,v = cv2.split(Cur)
    FH.write(np.frombuffer(np.getbuffer(y), dtype=np.uint8));
    u = cv2.resize(u, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    v = cv2.resize(v, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    FH.write(np.frombuffer(np.getbuffer(u), dtype=np.uint8))
    FH.write(np.frombuffer(np.getbuffer(v), dtype=np.uint8))  
    #print "YUV file written to file"
    
# EXAMPLE:
# resizeToHD(Sequ, "tmp/" + Sequ.BN + "_HDresized.yuv")
#==========================================
def resizeToHD(Sequ, Target_FN):
#==========================================

    YuvReader = CYuvReader(Sequ.AbsPath, Sequ.DimX, Sequ.DimY)

    # FOR ALL FRAMES --------------------------------------
    for POC in range(0,Sequ.Fr):
    #------------------------------------------------------  
        print "Resizing POC %d to HD, sharpening..." % POC
        (Y, U, V) = YuvReader.read_YUV()
        
        YUV = np.dstack((Y, U, V))
        RGB = cv2.cvtColor(YUV, cv2.COLOR_YUV2RGB)
        
        RGB = cv2.resize(RGB, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        
        Sharpened = cv2.GaussianBlur(RGB, (0, 0), 3)
        Sharpened = addWeighted(RGB, 1.5, Sharpened, -0.5, 0, Sharpened);
        #cv2.imwrite("tmp/TestHD.png", Sharpened)
        
        YUV = cv2.cvtColor(Sharpened, cv2.COLOR_RGB2YUV)
        YuvReader.write_YUV(Target_FN, YUV)
        
        a = 1
    
    YuvReader.close()
 
# EXAMPLE   
# createSequFromPNGs("/home/dom/Desktop/Version Michael/Denver3DHD_MZ", "Denver3DHD_MZ", "tmp/test", 200)
#==========================================
def createSequFromPNGs(PNGDir, PNG_BN, Target_DIRBN, NumFrames):
#==========================================
    #WARNING! INVERTED ORDER!

    FN = PNGDir + "/%s%04d.png" % (PNG_BN, 0)
    Img = cv2.imread(FN)
    DimY, DimX = Img.shape[:2]

    Target_FN = Target_DIRBN + "_%dx%d.yuv" % (DimX, DimY)
    FH = open(Target_FN, "wb")

    # FOR ALL FRAMES --------------------------------------
    #for POC in range(0,NumFrames):
    for POC in range(NumFrames-1,-1,-1):
    #------------------------------------------------------  
        FN = PNGDir + "/%s%04d.png" % (PNG_BN, POC)
        assert os.path.isfile(FN), "File not found: " + FN

        Img = cv2.imread(FN)
        Img = cv2.cvtColor(Img, cv2.COLOR_RGB2YUV)
        y,u,v = cv2.split(Img)
        
        FH.write(np.frombuffer(np.getbuffer(y), dtype=np.uint8));
        u = cv2.resize(u, (0, 0), fx=0.5, fy=0.5, interpolation=INTER_CUBIC)
        v = cv2.resize(v, (0, 0), fx=0.5, fy=0.5, interpolation=INTER_CUBIC)
        FH.write(np.frombuffer(np.getbuffer(u), dtype=np.uint8))
        FH.write(np.frombuffer(np.getbuffer(v), dtype=np.uint8))  
        print "%s written to %s" % (FN, Target_FN)
    
    FH.close()
        
# TODO: Get rid of this relict

#====================================================================================
class CYuvReader():
#====================================================================================

    #==========================================
    def __init__(self, Filename, DimX, DimY):
    #==========================================
        self.Filename = Filename
        self.DimX = DimX
        self.DimY = DimY
        
        self.FH = open(Filename, "rb")

        self.scaleX = 1 
        self.scaleY = self.scaleX
        
        self.FH.seek(0, os.SEEK_END)
        self.NumBytes = self.FH.tell()
        self.FH.seek(0, os.SEEK_SET)
        
        self.FrameSize = (self.DimX*self.DimY*1.5)

    #==========================================
    def read_Y(self):
    #==========================================
        #print "FTell: %d of %d" % (self.FH.tell(), self.NumBytes)
        Raw = self.FH.read(self.DimX*self.DimY)
        Y = Image.frombuffer('L', (self.DimX,self.DimY), Raw, 'raw', 'L', 0, 1)
        #print "Size raw:", len(Raw)
        #image.save("test.jpg")
        
        Cb = self.FH.read(self.DimX*self.DimY/4)
        Cr = self.FH.read(self.DimX*self.DimY/4)
        Y = np.array(Y)
        Y = cv2.resize(Y, (0, 0), fx=self.scaleX , fy=self.scaleY, interpolation=cv2.INTER_LINEAR)
        
        #cv2.imwrite("Img.jpg", Img)
        return  Y
    
    #==========================================
    def read_YUV(self):
    #==========================================
        #print "FTell: %d of %d" % (self.FH.tell(), self.NumBytes)
        Y_Raw = self.FH.read(self.DimX*self.DimY)
        U_Raw = self.FH.read(self.DimX*self.DimY/4)
        V_Raw = self.FH.read(self.DimX*self.DimY/4)
        
        Y = np.array(Image.frombuffer('L', (self.DimX,self.DimY),     Y_Raw, 'raw', 'L', 0, 1) )
        U = np.array(Image.frombuffer('L', (self.DimX/2,self.DimY/2), U_Raw, 'raw', 'L', 0, 1) )
        V = np.array(Image.frombuffer('L', (self.DimX/2,self.DimY/2), V_Raw, 'raw', 'L', 0, 1) )
        
        U = cv2.resize(U, (self.DimX, self.DimY), interpolation=cv2.INTER_CUBIC)
        V = cv2.resize(V, (self.DimX, self.DimY), interpolation=cv2.INTER_CUBIC)
        
        return  (Y, U, V)
    
    #==========================================
    def readPOC_Y(self, POC):
    #==========================================    
        last_pos = self.FH.tell() 
        self.FH.seek(POC*self.FrameSize, os.SEEK_SET)
        Y = self.read_Y()
        self.FH.seek(last_pos, os.SEEK_SET)
        return Y
        
    #==========================================
    def write_YUV(self, FN, YUV):
    #==========================================        
        FH = open(FN, "ab")
        y,u,v = cv2.split(YUV)
        FH.write(np.frombuffer(np.getbuffer(y), dtype=np.uint8));
        u = cv2.resize(u, (0, 0), fx=0.5, fy=0.5, interpolation=INTER_CUBIC)
        v = cv2.resize(v, (0, 0), fx=0.5, fy=0.5, interpolation=INTER_CUBIC)
        FH.write(np.frombuffer(np.getbuffer(u), dtype=np.uint8))
        FH.write(np.frombuffer(np.getbuffer(v), dtype=np.uint8))  
        print "YUV file written to file"
        FH.close()
    
    #==========================================
    def getNumFrames(self):
    #==========================================   
        return int(self.NumBytes/self.FrameSize)
    
    #==========================================
    def getResolution(self):
    #==========================================
        return (self.DimX*self.scaleX, self.DimY*self.scaleX)
    
    #==========================================
    def close(self):
    #==========================================
        self.FH.close()
