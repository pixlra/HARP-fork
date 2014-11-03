#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

#==========================================
# TYPE CASTS
#==========================================
# Img = np.uint8(Img)
# Integer data types: int8 int16 int32 int64 uint8 uint16 uint32 uint64    
# Float data types: float16  float32  float64     

#==========================================
def getNumBlocks(DimX, DimY, Blocksize):
#==========================================  
    NumMBsX = int(m.ceil(DimX / float(Blocksize)))
    NumMBsY = int(m.ceil(DimY / float(Blocksize)))
    return (NumMBsX, NumMBsY)

#==========================================
def getMin(Img):
#==========================================
    return np.amin(Img) #over all dimensions

#==========================================
def getAverage(Img):
#==========================================
    return np.average(Img) #over all dimensions
