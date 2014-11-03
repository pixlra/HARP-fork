#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
from Sequence import *
from OpenCV import *

# import os.path
# from os.path import basename
# import sys
# import numpy as np
# import shutil
# import copy
# import sys
# import time

#from General import *
#from Plot import *


#NOTES: for easy caculation of translations, everything is a 3x3 matrix
#NOTES: everything is relative! Hgg may be seen as Hss!
#NOTES: g: global origin, s: search origin, b: block origin

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class CWarper:
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    
    #==========================================
    def __init__(self):
    #==========================================
        pass
        self.BlockPos = np.eye(3, dtype=np.float32)
        self.Minus    = np.eye(3, dtype=np.float32)
        self.Minus[0,2] = -1.0 #will negate the BlockPos vector
        self.Minus[1,2] = -1.0 #will negate the BlockPos vector
    
    #==========================================
    def setBlockPos(self, BlockPosX, BlockPosY ):
    #==========================================
        self.BlockPos[0,2] = BlockPosX
        self.BlockPos[1,2] = BlockPosY
        
    #==========================================
    def getTransform_Hgg_to_Hgb(self, Hgg):
    #==========================================          
        # remember to init the BlockPos first (relative to origin)
        # transforms a gobal H_gg to a H_gb (REQUIRED FOR WARP-PERSECTIVE OF IMG TO BLOCK)
        # this H_gb allows to warp a small block locally, without black borders)
        # NOTE: it may be inefficient to use the whole image 
        # NOTE: it may be faster to introduce an intermediate (smaller) image
        # NOTE: this may cause problems! One would need to assume a "maximum" motion
        H_gb = np.dot(self.Minus*self.BlockPos, Hgg)#np.dot(Hgg, self.BlockPos))   
        return H_gb
    
    #==========================================
    def getTransform_Hgg_to_Hbb(self, Hgg):
    #==========================================          
        # remember to init the BlockPos first (relative to origin)
        # transforms a gobal H_gg to a H_bb (E.G. REQUIRED AS GROUND-TRUTH BETWEEN BLOCK IMAGES )
        # this H_gb allows to warp a small block locally, without black borders)
        # NOTE: it may be inefficient to use the whole image 
        # NOTE: it may be faster to introduce an intermediate (smaller) image
        # NOTE: this may cause problems! One would need to assume a "maximum" motion
        H_gb = np.dot(self.Minus*self.BlockPos, np.dot(Hgg, self.BlockPos))   
        return H_gb
    
#==========================================
def getH_fromMV(MV, Scale):
#==========================================   
    MV = [float(i)/Scale for i in MV] #convert to float, scale by 1/4
    H = np.eye(3, dtype=np.float32)
    H[0,2] = -MV[0]
    H[1,2] = -MV[1]
    return H

#==========================================     
def getWarped_Y(_Ref, H, TargetShape):             
#==========================================
    _WRPD_PU = warpPerspective(_Ref, H, TargetShape, flags=cv2.INTER_LINEAR, borderValue=(0))
    return _WRPD_PU    

#==========================================
def getWrpdLumDiff(Ref, Cur, H, Interp=cv2.INTER_CUBIC):
#==========================================
    
    (DimY, DimX) = Ref.shape[:2]
    if (len(Ref.shape) == 3):
        Y_Ref = Ref[:,:,0]
        Y_Cur = Cur[:,:,0]
    else:
        Y_Ref = Ref
        Y_Cur = Cur
    Y_ref_warped = cv2.warpPerspective(Y_Ref, H, (DimX, DimY), flags=Interp)
    DiffImg = np.uint8(cv2.addWeighted(np.float32(Y_Cur), 0.5, np.float32(Y_ref_warped), -0.5, 127))
    
#     DiffImg = cv2.multiply(DiffImg, alpha)
#     DiffImg = cv2.applyColorMap(DiffImg, cv2.COLORMAP_JET)
    
    return cv2.cvtColor(DiffImg, cv2.COLOR_GRAY2BGR)

#==========================================
def getWrpdOverlay(Ref, Cur, H, Interp=cv2.INTER_CUBIC):
#==========================================
    
    (DimY, DimX) = Ref.shape[:2]
    assert len(Ref.shape) == 3
    
    Ref_warped = cv2.warpPerspective(Ref, H, (DimX, DimY), flags=Interp,  borderMode=cv2.BORDER_CONSTANT, borderValue=WHITE)
    Overlay = np.uint8(cv2.addWeighted(np.float32(Cur), 0.5, np.float32(Ref_warped), 0.5, 0))
    
#     DiffImg = cv2.multiply(DiffImg, alpha)
#     DiffImg = cv2.applyColorMap(DiffImg, cv2.COLORMAP_JET)
    
    return Overlay

#==========================================
def getLumDiff(Ref, Cur):
#==========================================
    if len(Ref.shape) == 3: #we got several channels
        Y_Ref = Ref[:,:,0]
        Y_Cur = Cur[:,:,0]
    else:
        Y_Ref = Ref
        Y_Cur = Cur
    DiffImg = cv2.addWeighted(np.float32(Y_Cur), 0.5, np.float32(Y_Ref), -0.5, 127)
    DiffImg = DiffImg.astype(np.uint8)
    
    return DiffImg

#==========================================
def getSAD_Y(Ref, Cur):
#==========================================
    (DimY, DimX) = Ref.shape[:2]
    if len(Ref.shape) == 3: #we got several channels
        Y_Ref = Ref[:,:,0]
        Y_Cur = Cur[:,:,0]
    else:
        Y_Ref = Ref
        Y_Cur = Cur
    SAD = np.sum(np.abs(np.int16(Y_Cur) - np.int16(Y_Ref)))  
    Mean_SAD = np.float(SAD) / DimX / DimY; #unused
    return SAD
