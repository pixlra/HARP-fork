#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import re
import numpy as np

#look for: import re, re.search

# HOW TO ==================================
# 1) Paste line to https://pythex.org/
# 2) Create function to wrap
#==========================================

#==========================================
def get_DimX_DimY_from_Filename(FN):
#==========================================
    res = re.search(r"(\d*)x(\d*)", FN)
    return (np.int32(res.group(1)), np.int32(res.group(2)))

#==========================================
def fromStartToBracket(Str):
#==========================================
    res = re.search(r"::(.*)\sat", Str)
    return (res.group(1))


#get DimX and DimY from header in file
#         line = FH.readline()      
#         DimX = int( re.search(r"DimX=([-|\d]*)", line).group(1))
#         DimY = int( re.search(r"DimY=([-|\d]*)", line).group(1))
