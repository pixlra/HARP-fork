#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

#first import: dry run (indexer needs this)
try:
    import cv2     
    print "\nOpenCV: Version (dry run) = " + cv2.__version__                
except ImportError:
    print "\nOpenCV: no system installation found"
    pass

#import imp
#mypath = res("~/lib/OPENCV_2.4.9/lib/python2.6/site-packages/")
#fp, pathname, description = imp.find_module('cv2', [mypath])
#cv2 = imp.load_module('cv2', fp, pathname, description)

#==========================================
def import_OpenCV2():
#==========================================
    import imp
    global cv2
    
    #TODO: dedidacted OpenCV3 import function! cvdnarray code is only compatible with OpenCV2!
    
    def res(Dir): 
        return os.path.expandvars(os.path.expanduser(Dir))
    
    Locations = (#res("~/lib/OPENCV_3.0.0/lib/python2.7/dist-packages/"), #ubuntu OpenCV 3 experimental
                 res("~/lib/OPENCV_2.4.9/lib/python2.7/dist-packages/"), #ubuntu custom
                 res("~/lib/OPENCV_2.4.9/lib/python2.7/site-packages/"),  #suse custom
                 res("~/lib/OPENCV_2.4.9/lib/python2.6/site-packages/"),  #CentOS custom
                 res("/usr/lib64/python2.7/site-packages/"),  #suse system
                 res("/usr/lib/python2.7/site-packages/"),  #suse 32bit system
                 res("/usr/lib/python2.7/dist-packages/") )   #ubuntu system

    for Location in Locations:
        if os.path.isdir(Location): #we found a candidate
            fp, pathname, description = imp.find_module('cv2', [Location])
            cv2 = imp.load_module('cv2', fp, pathname, description)
            print "OpenCV Import from: " + Location
            #printHeadline("OpenCV Import from: " + Location)
            #print "OpenCV: Version (USED) = " + cv2.__version__ 
            return #return with first hit
    
    raise Exception("OpenCV not found. Sorry.")
    #from cv2 import *
    print "Imported import_OpenCV2, used version now is: " + cv2.__version__ 

import_OpenCV2()
from cv2 import *

#==========================================
def import_OpenCV3():
#==========================================
    import imp
    global cv2
    Location = res("~/lib/OPENCV_3.0.0/lib/python2.7/dist-packages/")
    assert os.path.isdir(Location)
    fp, pathname, description = imp.find_module('cv2', [Location])
    cv2 = imp.load_module('cv2', fp, pathname, description)
    print "OpenCV Import from: " + Location
    #from cv2 import *
    print "Imported import_OpenCV3, used version now is: " + cv2.__version__ 
    

#==========================================
# INTERPOLATION
#==========================================
# cv2.INTER_NEAREST
# cv2.INTER_LINEAR
# cv2.INTER_CUBIC

#==========================================
def printOpenCVFunctions():
#==========================================
    from inspect import getmembers, isfunction
    
    functions_list = [o for o in getmembers(cv2) if isfunction(o[1])] #returns empty list (why?)
    members = getmembers(cv2)
    print members
        
    return members

#==========================================
def testOpenCV_saveGrayImage():
#==========================================
    img = np.zeros((512,512,3), np.uint8)
    img = (128,128,128)
    cv2.line(img,(0,0),(511,511),(255,0,0),5)
    cv2.imwrite("testimage.jpg", img)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#==========================================
def printOpenCVOptions():
#==========================================
    flags = [i for i in dir(cv2) if i.startswith('COLOR_')]
    print flags
    
#==========================================
def getSpacer(Str, Img, Dim = 20):
#==========================================
    h, w = Img.shape[:2]
    if Str == "Vertical":
        VertSpacer = np.ones((h, Dim, 3), np.uint8)*255
        return VertSpacer
    elif Str == "Horizontal":
        HoriSpacer = np.ones((Dim,w, 3), np.uint8)*255
        return HoriSpacer

# #==========================================
# def RGBtoBGR(Img):
# #==========================================
#     return cv2.cvtColor(Img, cv2.COLOR_RGB2BGR)
# 
# #==========================================
# def BGRtoRGB(Img):
# #==========================================
#     return cv2.cvtColor(Img, cv2.COLOR_BGR2RGB)

#==========================================
def invertImage(Img):
#==========================================
    return (255 - Img)

#==========================================
def readImg(FN, Grayscale=False):  #load numpy matrix from file
#==========================================
    assertFileExists(FN, "Image file does not exist")
    Img = cv2.imread(FN,0) if  Grayscale else cv2.imread(FN)
    return Img



#==========================================
def writeImg(Img, FN):  #save image
#==========================================
    Img = cv2.cvtColor(Img, cv2.COLOR_RGB2BGR) # switch red and blue channels 
    if doInvert:
        Img = invertImage(Img)
    cv2.imwrite(FN, Img)
    
#==========================================
def saveY(Img, FN):  #save 1-channel PNG
#==========================================    
    cv2.imwrite(FN, Img[:,:,0])
    
#==========================================
def saveYUV(Img, FN):  #save YUV as RGB
#==========================================    
    cv2.imwrite(FN, cv2.cvtColor(Img, cv2.COLOR_YUV2RGB)) # switch red and blue channels 
    
#==========================================
def saveBGR(Img, FN):  #save OpenCV Image
#==========================================
    Img = invertImage(Img) if doInvert else Img
    cv2.imwrite(FN, Img)
    
#==========================================
def saveRGB(Img, FN):  #save numpy matrix as file
#==========================================
    Img = cv2.cvtColor(Img, cv2.COLOR_RGB2BGR) # switch red and blue channels 
    Img = invertImage(Img) if doInvert else Img
    cv2.imwrite(FN, Img)
    
#==========================================
def resizeToWidth(Img, Width, Interp=cv2.INTER_LINEAR):
#==========================================
    (rows, cols) = Img.shape[:2]
    RatioX = float(cols)/Width;
    Height = int(rows/RatioX);
    return cv2.resize(Img, (Width, Height), interpolation=Interp)

#==========================================
def drawString(dst, (x, y), s):
#==========================================
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)

#==========================================
def writeText(Img, (x, y), Text, Size=1.0, Color=(255, 255, 255)):
#==========================================
    cv2.putText(Img, Text, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, Size, Color, thickness = 2, lineType=cv2.CV_AA)
    #cv2.putText(Img, Text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)

#==========================================
class CImageMatrix():
#==========================================

    #==========================================
    def __init__(self, MatrixRows, MatrixCols, DimX, DimY):
    #==========================================
        self.DimX = DimX
        self.DimY = DimY
        self.MatrixRows = MatrixRows
        self.MatrixCols = MatrixCols
        
        self.Final = np.zeros((MatrixRows*DimY,MatrixCols*DimX,3), np.uint8)
    
    #==========================================
    def fillPosition(self, Image, Row, Col, text = None, CustomDimY = -1, CustomDimX = -1):
    #==========================================
        if CustomDimY == -1 or CustomDimX == -1:
            self.CustomDimY = self.DimY;
            self.CustomDimX = self.DimX;

        ImgClone = Image.copy()
        if len(ImgClone.shape) != 3: #if no channel information given, i.e. grayscale
            ImgClone = cv2.cvtColor(ImgClone, cv2.COLOR_GRAY2RGB)
        drawText(ImgClone, (10,20), text)
        #drawText(self.Final, (50,50), text)

        d = 2
        self.Final[Row*self.DimY:Row*self.DimY+self.DimY, Col*self.DimX:Col*self.DimX+self.DimX] = ImgClone
        
    #==========================================
    def getFinal(self):
    #==========================================
#        return self.Final
        Resized = cv2.resize(self.Final, (0, 0), 
                          fx=1920.0/(self.DimX*self.MatrixCols*1.2), 
                          fy=1080.0/(self.DimY*self.MatrixRows*1.2), interpolation=cv2.INTER_LINEAR)
        
        if invertImages:
            Resized = invertImage(Resized)
            
        return Resized
    
#==========================================
def test_CImageMatrix():
#==========================================

    #ImageMatrix example
    ImgMatrix = CImageMatrix(2, 2, 1280, 720)
    test = np.zeros((720,1280,3), np.uint8)
    ImgMatrix.fillPosition(test, 0, 0, "Hello World")
    cv2.imshow("Test", ImgMatrix.getFinal())
    cv2.waitKey()
    
#==========================================
if __name__ == '__main__':
#==========================================
    #sys.exit(0)
    members = printOpenCVFunctions()
    for member in members:
        logText(str(member), "./OpenCV_members.txt")
    #print "\n".join(members)
    #writeStringToFN(str(members), "./OpenCV_members.txt")
    

    
