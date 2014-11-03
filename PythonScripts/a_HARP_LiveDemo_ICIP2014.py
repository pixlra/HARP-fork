#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer, Wolfgang Schnurrer
# File licensed under GNU GPL (see HARP_License.txt)

import sys, os
__builtins__.ProjectDir = os.path.abspath("../")
assert( "HARP" in os.path.basename(ProjectDir) )
__builtins__.LibDir = ProjectDir + "/PythonLib"
__builtins__.TmpDir = ProjectDir + "/tmp"
sys.path.append(LibDir) 

# GLOBAL SETTINGS, CHANGE HERE --------------------------------
X265_BinDir   = ProjectDir + "/bin/Demo/x265_64Bit"
#X265_BinDir   = "/home/lnt335/HARP/HARP"
VideoSrc = 0 # V4L2 video source
isVirtualCam = False #for debugging
# -------------------------------------------------------------
os.environ["LD_LIBRARY_PATH"] = X265_BinDir 

from Imports_Basic import *
from OpenCV import *
from System import *
from Sequence import *
from Warp import *

from GUI.ShowPOC import *
from GUI.AnalyzePOC import *
from Encoder.X265_Encoder import *
from Encoder.HM_Encoder import *

# OPENCV VIDEO
import sys, os
sys.path.append(ProjectDir + "/Various/ThirdParty")
import opencv.video #third party

# PYQTGRAPH
from PyQt4 import QtGui  #force PyQt

for gs in ['raster', 'native', 'opengl']: # force specific graphics system
    if gs in sys.argv:
        QtGui.QApplication.setGraphicsSystem(gs)
        break

from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
from pyqtgraph.dockarea import *

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

from PyQt4.QtCore import * #reimport since pyqtgraph runs: "from PyQt4 import QtCore, QtGui"
from PyQt4.QtGui import *
# END PYQTGRAPH

cam = None
Ref = None
Cur = None
DimX = None
DimY = None





#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class VirtualCam(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #==========================================
    def __init__(self):
    #==========================================
        super(VirtualCam, self).__init__()
        # CHANGE HERE -------------------------------------------------
        # -------------------------------------------------------------
        self.Images = []
        
        Img0 = readImg(ProjectDir + "/Various/Resources/Tohajiilee.jpg")
        Img0 = cv2.resize(Img0, (640, 480), interpolation=cv2.INTER_LINEAR)
        
        Img1 = readImg(ProjectDir + "/Various/Resources/Tohajiilee_rotated.jpg")
        Img1 = cv2.resize(Img1, (640, 480), interpolation=cv2.INTER_LINEAR)
        
        self.Images.append(Img0)
        self.Images.append(Img1)
        self.toggle = 0

    #==========================================
    def read(self):
    #==========================================
        if self.toggle == 0:
            Image = self.Images[0]
        else : Image = self.Images[1]
        self.toggle = not self.toggle
        time.sleep(0.015)
        return None, Image

    #==========================================
    def release(self):
    #==========================================        
        pass


#==========================================
def startGrabbing():
#==========================================
    global VideoSrc
    global cam
    global DimX, DimY
    global Ref, Cur
    global ThreadLock
    global StopGrabbingThread
    global isVirtualCam
    if isVirtualCam:
        cam = VirtualCam()
    else:
        cam = opencv.video.create_capture(VideoSrc)
    
    
    #-------------------------------------
    # RETRIEVE CAM INFOS
    #-------------------------------------   
    ret, frame = cam.read() 
    
    DimY, DimX = frame.shape[:2]
    print "\nWebcam resolution: %dx%d\n" % (DimX, DimY)
    
    cnt = 0
    while(not StopGrabbingThread):  
          
        ret, TmpRefRGB = cam.read()
        
        ThreadLock.acquire()
        for x in range(0, 4):
            ret, test = cam.read()
            
        ret, TmpCurRGB = cam.read()
        
        TmpCur = cv2.cvtColor(TmpCurRGB, cv2.COLOR_RGB2YUV)
        TmpRef = cv2.cvtColor(TmpRefRGB, cv2.COLOR_RGB2YUV)
        
        Ref = TmpRef
        Cur = TmpCur
        #MSEC = cam.get(cv2.cv.CV_CAP_PROP_FPS)
        if cnt % 100 == 0:
            print "Webcam captured: %d pairs" % cnt
        cnt += 1
        ThreadLock.release()
             
#==========================================
def stopGrabbing():
#==========================================
        global cam
        global StopGrabbingThread
        StopGrabbingThread = True
        
        ThreadLock.acquire() 
        cam.release()
        ThreadLock.release()


GrabbingThread = threading.Thread(target=startGrabbing)
GrabbingThread.daemon = False
GrabbingThread.start()
ThreadLock = threading.Lock() 
StopGrabbingThread = False


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class Demo(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self, GUI):
    #==========================================
        super(Demo, self).__init__()
        # CHANGE HERE -------------------------------------------------
        # -------------------------------------------------------------
        self.GUI = GUI
        self.p0 = None
        self.use_ransac = True
        
        os.chdir(TmpDir)
        
    #==========================================
    def processFramePair(self, Ref, Cur):
    #==========================================
        QP = self.GUI.p.param('Basic settings', 'QP').value()
        if QP>50:
            QP=50
        if QP<1:
            QP=1
        QP = round(QP)		
        self.GUI.p.param('Basic settings', 'QP').setValue(QP)


        isX265 = self.GUI.p.param('Basic settings', 'x265').value()
        
        DimY, DimX = Ref.shape[:2]
        assert(DimX == 640 and DimY == 480)
        
        self.starttime = time.time()                
        FN_YUV = TmpDir + "/webcam_%dx%d.yuv" % ( DimX, DimY)
        outfile = open(FN_YUV, "w")

        #--------------------------------------
        # CREATE YUV (2 FRAMES)
        #--------------------------------------
        write_YUV(outfile, Ref)
        write_YUV(outfile, Cur)
        outfile.close()
        
        Sequ = Sequence(FN_YUV, Fr=2, FPS=30)
            
        #--------------------------------------
        # RUN X265 ENCODER
        #--------------------------------------
        if isX265:
            global X265_BinDir
            EncBin = X265_BinDir + "/x265"
            INI_FN = ProjectDir + "/PythonLib/Encoder/X265_Settings.ini"   
            assert os.path.isfile(INI_FN), "INI file not found: " + INI_FN
    
            Encoder = X265_Encoder( OutputDir=TmpDir, Passport="007", 
                                    Name="X265", InfoStr="_Test", 
                                    EncBin=EncBin, DecBin=None, INI_FN=INI_FN, OverrideStr="", 
                                    Sequ=Sequ, QP=QP,
                                    PSNR_Tool=None)
            
            EncoderCmd = Encoder.get_CommandLineCall()
            print "EncoderCmd: " + EncoderCmd      
            
            assert os.system(EncoderCmd)==0, "encoder cmd failed" 
        else:
        #--------------------------------------
        # RUN HM ENCODER
        #--------------------------------------
            EncBin = ProjectDir + "/bin/TAppEncoder"
            INI_FN = ProjectDir + "/PythonLib/Encoder/HM_Encoder.ini"   
            assert os.path.isfile(INI_FN), "INI file not found: " + INI_FN
    
            Encoder = HM_Encoder( OutputDir=TmpDir, Passport="007", 
                                    Name="HMEnc", InfoStr="_Test", 
                                    EncBin=EncBin, DecBin=None, INI_FN=INI_FN, OverrideStr="", 
                                    Sequ=Sequ, QP=QP,
                                    PSNR_Tool=None)
            
            EncoderCmd = Encoder.get_CommandLineCall()
            EncoderCmd += " --HARP_TmpDir=." 
            print "EncoderCmd: " + EncoderCmd 
            #DecoderCmd += " --HARP_PUs" #debug     
            
            assert os.system(EncoderCmd)==0, "encoder cmd failed" 
                
        #--------------------------------------
        # RUN HM DECODER
        #--------------------------------------
        DecoderCmd = ProjectDir + "/bin/TAppDecoder -b " + Encoder.bitstream + " -o decoded.yuv --HARP_TmpDir=. "
        #DecoderCmd += " --HARP_PUs" #debug
        assert os.system(DecoderCmd)==0, "decoder cmd failed" 
        
        #-------------------------------------
        # LOADING DECODER PKL
        #-------------------------------------
        print "LOADING DECODER PKL"
        POCIdx = 0
        FN = TmpDir + "/" + "PyPOC_%05d.pkl" % POCIdx
        assert os.path.exists(FN), "PWD: %s, missing FN: %s" % (os.getcwd(), FN)
        POC_Intra = pickle.load(open(FN, "rb" ) )   
        POCIdx = 1
        FN = TmpDir + "/" + "PyPOC_%05d.pkl" % POCIdx
        assert os.path.exists(FN), "PWD: %s, missing FN: %s" % (os.getcwd(), FN)
        POC_Inter = pickle.load(open(FN, "rb" ) )   
        
        #self.GUI.p.param('Basic settings', 'Show CUs').setOpts(readonly=False, enabled=True)
        Show_CUs = self.GUI.p.param('Basic settings', 'Show CUs').value()
        Show_PUs = self.GUI.p.param('Basic settings', 'Show PUs').value()
        Show_Modes = self.GUI.p.param('Basic settings', 'Show Modes').value()

        #self.GUI.p.param('Basic settings', 'Show CUs').setValue(not self.GUI.p.param('Basic settings', 'Show CUs').value())
        
        
        self.ShowPOC_Intra = ShowPOC(POC_Intra, Show_CUs, Show_PUs, Show_Modes)
        self.ShowPOC_Intra.visualize()

        self.ShowPOC_Inter = ShowPOC(POC_Inter, Show_CUs, Show_PUs, Show_Modes)
        self.ShowPOC_Inter.visualize()
        
        self.AnalyzePOC_Inter = AnalyzePOC(POC_Inter)
        self.AnalyzePOC_Inter.analyze()
        

        
        
        #cv2.imwrite(TmpDir + "/VizPUs.jpg", VizPUs) 


        #--------------------------------------
        # TIMING
        #--------------------------------------            
        NumSecs = (time.time() - self.starttime)
        FPS = 1 / NumSecs
        print "\nFPS = %f \n ------------------ \n" % FPS     
        
    #==========================================
    def run(self):
    #==========================================
        try :
            global Ref
            global Cur
            
            #-------------------------------------
            # FOR ALL RUNS
            #-------------------------------------
            NumRuns = 1000
            for myrun in np.arange(NumRuns):
                self.processFramePair(Ref, Cur, 15)
                cv2.imshow('frame', self.VizPUs)
                cv2.waitKey(1)
       
            stopGrabbing()
            cv2.destroyAllWindows()
            
        except Exception, Str: #prevent V4L2 to eat the webcam
            import traceback
            print "Exception!"
            stopGrabbing()
            cv2.destroyAllWindows()
            print "EXCEPTION------------------------"
            print "Unexpected ERROR:", sys.exc_info()[0]
            traceback.print_tb(sys.exc_info()[2])
            print Str  
            print "---------------------------------"
            raise




#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class GUIMainWindow(QtGui.QMainWindow):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #==========================================
    def __init__(self):
    #==========================================
        super(GUIMainWindow, self).__init__()
        
        # CHANGE HERE -------------------------------------------------
        # -------------------------------------------------------------

        area = DockArea()
        self.setCentralWidget(area)
        self.resize(1280, 800)
        self.setWindowTitle('Demo: How to use HARP with Python')
        
        ## Create docks, place them into the window one at a time.
        ## Note that size arguments are only a suggestion; docks will still have to
        ## fill the entire dock area and obey the limits of their internal widgets.
        d1 = Dock("Control", size=(300,200))     ## give this dock the minimum possible size
        d2 = Dock("Description", size=(300,800))
        d31 = Dock("INTRA frame - Prediction Units", size=(500,300))
        d32 = Dock("INTER frame - Prediction Units", size=(500,300))
        #d33 = Dock("Dock3 - Transform Units", size=(500,300))
        d41 = Dock("Frame Difference ", size=(100,100))
        d42 = Dock("Current Frame ", size=(100,100))
        d51 = Dock("CU Depths", size=(200,100))
        d52 = Dock("MVs X Component", size=(200,100))
        d53 = Dock("MVs Y Component", size=(200,100))

        area.addDock(d2, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
        area.addDock(d1, 'bottom', d2)     ## place d2 at right edge of dock area
        area.addDock(d31, 'right')     
        area.addDock(d32, 'bottom', d31)
        #area.addDock(d33, 'bottom', d32)
        area.addDock(d41, 'right')
        area.addDock(d51, 'bottom', d41) 
        area.addDock(d42, 'right', d41)
        
        area.addDock(d52, 'right', d51)
        area.addDock(d53, 'right', d52)
           
        #==========================================
        def dock_ImageItem(self, Dock):
        #==========================================
            pgGLWidget = pg.GraphicsLayoutWidget()
            ViewBox = pgGLWidget.addViewBox(invertY = True)
            #ViewBox.setBackgroundColor((255,255,255))
            ViewBox.setAspectLocked(True)
            pgImageItem = pg.ImageItem(border='w')
            ViewBox.addItem(pgImageItem)
            Dock.addWidget(pgGLWidget)
            return pgImageItem
        
        #==========================================
        def dock_CurveItem(self, Dock, Title, LabelX, LabelY):
        #==========================================
            pgGWindow= pg.GraphicsLayoutWidget()
            pgPlot = pgGWindow.addPlot(title=Title)
            x =[0,0,0]
            y = [0,0]
            pgCurveItem = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 80))
            pgPlot.addItem(pgCurveItem)
            pgPlot.setLabel('bottom', LabelX)
            pgPlot.setLabel('left', LabelY)
            Dock.addWidget(pgGWindow)
            return pgCurveItem

        
        self.ImageItem_d2  = dock_ImageItem(self, d2)
        self.ImageItem_d31 = dock_ImageItem(self, d31)
        self.ImageItem_d32 = dock_ImageItem(self, d32)
        self.ImageItem_d41 = dock_ImageItem(self, d41)
        self.ImageItem_d42 = dock_ImageItem(self, d42)
          
        
        self.CurveItem_d51 = dock_CurveItem(self, d51, "CU Depths",       "CU Depth", "Number of Occurences")
        self.CurveItem_d52 = dock_CurveItem(self, d52, "MVs X Component", "Magnitude", "Number of Occurences")
        self.CurveItem_d53 = dock_CurveItem(self, d53, "MVs Y Component", "Magnitude", "Number of Occurences")
          
        params = [
            {'name': 'Basic settings', 'type': 'group', 'children': 
             [
                {'name': 'QP', 'type': 'int', 'value': 30},
                {'name': 'x265', 'type': 'bool', 'value': True},
                {'name': 'Show CUs', 'type': 'bool', 'value': True},
                {'name': 'Show PUs', 'type': 'bool', 'value': True},
                {'name': 'Show Modes', 'type': 'bool', 'value': True},
            ]},

            ]
        
        ## Create tree of Parameter objects
        p = Parameter.create(name='params', type='group', children=params, readonly=False, enabled=True)
        t = ParameterTree()
        t.setParameters(p, showTop=False)
        t.setWindowTitle('pyqtgraph example: Parameter Tree')
        self.p = p
        d1.addWidget(t)
        
        MyWorkThread = WorkThread(self)
        MyWorkThread.start()
        
        Description = readImg(ProjectDir + "/Various/Resources/Special/LMS_Demo.png")
        Description = cv2.transpose(cv2.cvtColor(Description, cv2.COLOR_BGR2RGB))
    
        self.ImageItem_d2.setImage(Description, autoDownsample=True, border=(255,255,255) )
        
#         pic = QtGui.QLabel()
#         #pic.setGeometry(0, 0, 400, 400)
#         #use full ABSOLUTE path to the image, not relative
#         pic.setPixmap(QtGui.QPixmap(ProjectDir + "/Various/Resources/DemoChain.png"))
#         pic.setMaximumWidth(300)
#         pic.setMaximumHeight(300)
#         d2.addWidget(pic)
        
        
#     #==========================================
#     def __del__(self):
#     #==========================================  
#         stopGrabbing()
#         super(GUIMainWindow, self).__del__()      
  
    #==========================================        
    # @Slot()      
    def closeEvent(self,event):
    #==========================================
        result = QtGui.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
        event.ignore()

        if result == QtGui.QMessageBox.Yes:
            stopGrabbing()
            event.accept()
            
            #sys.exit(0)

    #==========================================        
    # @Slot()
    def slot_Update(self, update_tuple):
    #==========================================
    
        #(Intra, Inter, LumDiff, CurCopy, CU_Depths))

        self.ImageItem_d31.setImage(update_tuple[0])
        self.ImageItem_d32.setImage(update_tuple[1])
        self.ImageItem_d41.setImage(update_tuple[2])
        self.ImageItem_d42.setImage(update_tuple[3])
        
        y,x = np.histogram(update_tuple[4], bins=[0, 1, 2, 3, 4])
            #self.MV_x_Histo.setData(x,y)
            #self.curve = self.GUI.PlotHisto.plot(pen='y')
        self.CurveItem_d51.setData(x,y)
        
        y,x = np.histogram(update_tuple[5], bins=np.linspace(-30*6, 30*6, 80))
        self.CurveItem_d52.setData(x,y)
        
        y,x = np.histogram(update_tuple[6], bins=np.linspace(-30*6, 30*6, 80))
        self.CurveItem_d53.setData(x,y)
        
        
        print "Result ready"


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||        
class WorkThread(QtCore.QThread):
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| 

    signal_Update = Signal(object)
   
    #==========================================    
    def __init__(self, rGUIMainWindow):
    #==========================================    
        QtCore.QThread.__init__(self)
        self.Demo = Demo(rGUIMainWindow)
        self.GUI = rGUIMainWindow

#     #========================================== 
#     def __del__(self):
#     #========================================== 
#         self.wait()
        
    #========================================== 
    def run(self):
    #========================================== 
        try :
     
            global ThreadLock
            global Ref
            global Cur
            
            
            self.signal_Update.connect(self.GUI.slot_Update)
            
            while(1):
                ThreadLock.acquire() 
                RefCopy = np.copy(Ref)
                CurCopy = np.copy(Cur)
                ThreadLock.release()
                    
                self.Demo.processFramePair(RefCopy, CurCopy)
                
                CU_Depths = np.copy(self.Demo.AnalyzePOC_Inter.CU_Depths)
                MV_x = np.copy(self.Demo.AnalyzePOC_Inter.MV_x)
                MV_y = np.copy(self.Demo.AnalyzePOC_Inter.MV_y)
    
                Intra = cv2.transpose(cv2.cvtColor(self.Demo.ShowPOC_Intra.Final, cv2.COLOR_BGR2RGB))
                Inter = cv2.transpose(cv2.cvtColor(self.Demo.ShowPOC_Inter.Final, cv2.COLOR_BGR2RGB))
                LumDiff = getLumDiff(RefCopy, CurCopy)
                LumDiff = cv2.transpose(LumDiff)
                    
                CurCopy = cv2.transpose(cv2.cvtColor(CurCopy, cv2.COLOR_YUV2BGR)) 
                
                self.signal_Update.emit((Intra, Inter, LumDiff, CurCopy, CU_Depths, MV_x, MV_y))
                
            self.terminate()   
              


        except Exception, Str: #prevent V4L2 to eat the webcam
            import traceback
            print "---- EXCEPTION! ----"
            print "ERROR:", sys.exc_info()[0]
            traceback.print_tb(sys.exc_info()[2])
            print Str  
            print "---------------------------------"
            stopGrabbing()
            #cv2.destroyAllWindows()
            sys.exit(0)  
        
#==========================================
if __name__ == '__main__':
#==========================================    
    try :
        import signal
        def signal_handler(signal, frame):
            print 'You pressed Ctrl+C!'
            stopGrabbing()
            cv2.destroyAllWindows()
            time.sleep(1)
            sys.exit(0)
    
        signal.signal(signal.SIGINT, signal_handler)
        
        time.sleep(2) #give webcam some time
        app = QtGui.QApplication([])
        app.setQuitOnLastWindowClosed(True)
        MainWindow = GUIMainWindow()
        MainWindow.show()
        QtGui.QApplication.instance().exec_()
    
    except Exception, Str: #prevent V4L2 to eat the webcam
	    import traceback
	    print "---- EXCEPTION! ----"
	    print "ERROR:", sys.exc_info()[0]
	    traceback.print_tb(sys.exc_info()[2])
	    print Str  
	    print "---------------------------------"
	    stopGrabbing()
	    #cv2.destroyAllWindows()
	    sys.exit(0) 
    
