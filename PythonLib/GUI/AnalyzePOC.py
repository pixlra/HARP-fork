#!/usr/bin/env python
# coding: utf8

# (c) 2014 Lena Förstel
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
from System import *
from OpenCV import *

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class AnalyzePOC(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    #==========================================
    def __init__(self, POC):
    #==========================================

        super(AnalyzePOC, self).__init__()
        
        # CHANGE HERE -------------------------------------------------

        # ------------------------------------------------------------- 
        
        self.POC = POC
        self.CU_Depths = []
        self.MV_x = []
        self.MV_y = []
        

    #==========================================
    def analyze(self):
    #==========================================
        
        #-------------------------------------
        # PREPARATIONS
        #-------------------------------------   
        POC = self.POC     
        DimX, DimY = self.POC["Size"]
        
        #-------------------------------------
        # Iterating
        #-------------------------------------
        for CTU in POC["CTUs"]:
            for CU in CTU["CUs"]:

                self.CU_Depths.append(CU["Depth"])
                
                for PU in CU["PUs"]: 
                    if CU["Mode"] != "Intra": 
                        if PU["MV"][0]  == PU["MV"][1] == 0:
                            continue
                        self.MV_x.append(PU["MV"][0])
                        self.MV_y.append(PU["MV"][1])
                        
        print "AnalyzePOC: analysis done"


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
    myAnalyzePOC = AnalyzePOC(POC)
    myAnalyzePOC.analyze()
    
    
    
