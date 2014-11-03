#!/usr/bin/env python
# coding: utf8

# (c) 2014 Lena Förstel
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
from System import *
from OpenCV import *

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class ShowPOC(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self, POC, CU_borders, PU_borders, mode_colour):
    #==========================================

        super(ShowPOC, self).__init__()
        
        # CHANGE HERE -------------------------------------------------
        width_MV  = 3
        line_width = 5
        PU_line_colour = WHITE
        self.scale = 3
        # ------------------------------------------------------------- 
        
        self.POC = POC
        self.thickness_MV = width_MV
        self.line_width = line_width
        self.PU_line_colour = PU_line_colour
        self.CU_borders = CU_borders
        self.PU_borders = PU_borders
        self.mode_colour = mode_colour
        

    #==========================================
    def visualize(self):
    #==========================================
        
        
        #-------------------------------------
        # PREPARATIONS
        #-------------------------------------   
        POC = self.POC     
        DimX, DimY = self.POC["Size"]
        
        Y = np.zeros((64*self.POC["Size_inCTUs"][1],64*self.POC["Size_inCTUs"][0],3 ),np.uint8)
        
        Y[0:DimY,0:DimX,0] = self.POC["YuvRec"]["Y"]
        Y[0:DimY,0:DimX,1] = self.POC["YuvRec"]["Y"]
        Y[0:DimY,0:DimX,2] = self.POC["YuvRec"]["Y"]
        
        #Create a white image
        self.VizPUs = np.ones((64*self.POC["Size_inCTUs"][1],64*self.POC["Size_inCTUs"][0],3), np.uint8)
        self.VizPUs = self.VizPUs*255
        
        #-------------------------------------
        # UPSCALING
        #-------------------------------------
        scale = self.scale
        DimX = DimX * scale
        DimY = DimY * scale
        #self.VizPUs = cv2.resize(self.VizPUs, (DimX, DimY), interpolation=cv2.INTER_LINEAR)
        #Y = cv2.resize(Y, (DimX, DimY), interpolation=cv2.INTER_LINEAR)
        self.VizPUs = cv2.resize(self.VizPUs, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        Y = cv2.resize(Y, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        
        #-------------------------------------
        # DRAWING CUs and PUs
        #-------------------------------------
        for CTU in POC["CTUs"]:
            for CU in CTU["CUs"]:
            
                self.drawCU(CU)
                Size = CU["Size"]*scale
                Depth = CU["Depth"]
       
            str = "%d" % CTU["Idx"]    
            font = cv2.FONT_HERSHEY_PLAIN   
            Pos_CTU = CTU["Pos"][0]*scale, CTU["Pos"][1]*scale
            cv2.putText(self.VizPUs,str,(Pos_CTU[0]+5,Pos_CTU[1]+20), font, 1.2,YELLOW,1) # text: CTU index
            
        #-------------------------------------
        # DRAWING MVs
        #------------------------------------- 
        for CTU in POC["CTUs"]:
            for CU in CTU["CUs"]:  
                for PU in CU["PUs"]:  
                    self.drawMV(PU)
                    
        #-------------------------------------
        # BLENDING
        #-------------------------------------
        WeightA = 0.5
        WeightB = 1.0 - WeightA
        self.Final = np.uint8(self.VizPUs * WeightA + Y * WeightB) 
        self.Final = self.Final[0:DimY,0:DimX,:]
        
        #cv2.imwrite("VizPUs.jpg", self.VizPUs)              

    
    #==========================================
    def drawCU(self, CU): 
    #==========================================
        s = self.scale
        Pos = CU["Pos"][0]*s, CU["Pos"][1]*s
        Size = CU["Size"][0]*s, CU["Size"][1]*s
        Mode = CU["Mode"]
        Col = GRAY
        Depth = CU["Depth"]
                
        for PU in CU["PUs"]:
            self.drawPU(PU,Mode)
              
        if self.CU_borders ==1:     # draw CU borders black
            cv2.rectangle(self.VizPUs,(Pos[0],Pos[1]),(Pos[0]+Size[0],Pos[1]+Size[1]),(0,0,0),self.line_width)  

    #==========================================
    def drawPU(self, PU, Mode):
    #==========================================
        s = self.scale
        Pos_PU = PU["Pos"][0]*s,PU["Pos"][1]*s
        Size_PU = PU["Size"][0]*s,PU["Size"][1]*s
        
        if Mode == "Intra": 
            Col= RED #set red
        elif Mode == "Inter": 
            Col= BLUE #set blue
        elif Mode == "Merge":
            Col= DARKGREEN #set darkgreen
        elif Mode == "Skip":
            Col= GREEN #set light green
        else: assert(0)

        if self.mode_colour == 1:
            cv2.rectangle(self.VizPUs, (Pos_PU[0],Pos_PU[1]), (Pos_PU[0]+Size_PU[0], Pos_PU[1]+Size_PU[1]), Col, -1)
            
        #special case: set "white" PU to gray so we can set white PU borders AND black CU borders
        if (self.mode_colour == 0) and (self.PU_line_colour==WHITE):
            cv2.rectangle(self.VizPUs, (Pos_PU[0],Pos_PU[1]), (Pos_PU[0]+Size_PU[0], Pos_PU[1]+Size_PU[1]), GRAY, -1)
        
        if self.PU_borders == 1:    
            cv2.rectangle(self.VizPUs, (Pos_PU[0],Pos_PU[1]), (Pos_PU[0]+Size_PU[0], Pos_PU[1]+Size_PU[1]), self.PU_line_colour, self.line_width-1)
      
    #==========================================    
    def drawMV(self, PU, ): 
    #==========================================
        s = self.scale
        
        if 'MV' not in PU:
            return
        
        MV_PU =  PU["MV"][0]*s, PU["MV"][1]*s
        Pos_PU = PU["Pos"][0]*s, PU["Pos"][1]*s
        Size_PU = PU["Size"][0]*s, PU["Size"][1]*s

        arrow_magnitude=5
        line_type=8
        shift=0

        start = np.asarray(Pos_PU) + np.asarray(Size_PU) / 2.0 #centering in PU
        end   = start + np.asarray(MV_PU) / 4.0
        
        start = start.astype(int)
        end   = end.astype(int)

#         start = (int(start[0]), int(start[1])) #to int
#         end = (int(end[0]), int(end[1])) #to int
        p, q = tuple(start), tuple(end)
        color = tuple(GREEN)
        cv2.line(self.VizPUs, p, q, color, self.thickness_MV, line_type, shift) # draw arrow tail
        
        angle = np.arctan2(p[1]-q[1], p[0]-q[0]) # calc angle of the arrow 
        
        p = (int(q[0] + arrow_magnitude * np.cos(angle + np.pi/4.0)), # starting point of first line of arrow head
        int(q[1] + arrow_magnitude * np.sin(angle + np.pi/4.0)))
        cv2.line(self.VizPUs, p, q, color, self.thickness_MV, line_type, shift) # draw first half of arrow head
        
        p = (int(q[0] + arrow_magnitude * np.cos(angle - np.pi/4.0)), # starting point of second line of arrow head
        int(q[1] + arrow_magnitude * np.sin(angle - np.pi/4.0)))
        cv2.line(self.VizPUs, p, q, color, self.thickness_MV, line_type, shift) # draw second half of arrow head
        
        
#         if MV_PU[0] != 0:
#             arg=MV_PU[1]/MV_PU[0]     
#             angle = np.arctan(arg)
#         else:
#             angle = np.pi/2   
#            
#         strt = list(Pos_PU)
#         end = list(MV_PU)
#         strt[0] = strt[0]+Size_PU[0]/2
#         strt[1] = strt[1]+Size_PU[1]/2
#         end[0] = end[0]/4+strt[0]
#         end[1] = end[1]/4+strt[1]
#         P2 = end
#         P3 = end
#         d = 3.46
#         b = np.pi/7
#         cv2.line(self.VizPUs,(strt[0],strt[1]),(end[0],end[1]),(0,255,0),1)
#         
# #         P2 = end[0]-4, end [1] +2
# #         P3 = end[0]-4, end [1] -2
#               
#         P2 = end[0]-int(d*np.sin(np.pi/4-angle-b)),end[1]+int(d*np.cos(np.pi/4-angle-b))
#         P3 = end[0]-int(d*np.cos(angle-b)),end[1]+int(d*np.sin(angle-b))
#            
#         pts = np.array([[end[0],end[1]],[P2[0],P2[1]],[P3[0],P3[1]]], np.int32)
#         pts = pts.reshape((-1,1,2))
#         cv2.fillPoly(self.VizPUs, [pts], (0,255,0))
         


#==========================================
if __name__ == '__main__':
#==========================================    
    import sys, os
    __builtins__.ProjectDir = os.path.abspath("../../")
    assert( "HARP" in os.path.basename(ProjectDir) )
    __builtins__.LibDir = ProjectDir + "/PythonLib"
    __builtins__.TmpDir = ProjectDir + "/tmp"
    sys.path.append(LibDir) 
    
    #-------------------------------------
    # LOADING PKL
    #-------------------------------------
    POCIdx = 1
    Prefix = "PyPOC_"
    FN = TmpDir + "/" + Prefix + "%05d.pkl" % POCIdx
    
    assert os.path.exists(FN), "PWD: %s, missing FN: %s" % (os.getcwd(), FN)
    POC = pickle.load(open(FN, "rb" ) )   
    print "PICKLE loaded: " + FN
    myShowPOC = ShowPOC(POC, 1, 1, 1)
    VizPUs = myShowPOC.visualize()
    cv2.imwrite(TmpDir + "/VizPUs.jpg", VizPUs) 
    
    
