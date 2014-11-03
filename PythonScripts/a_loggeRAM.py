#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import matplotlib # forcing to use Agg backend!
matplotlib.use('Agg')
import matplotlib.pyplot as plt


import sys, os
__builtins__.ProjectDir = os.path.abspath("../")
assert( "HARP" in os.path.basename(ProjectDir) )
__builtins__.LibDir = ProjectDir + "/PythonLib"
__builtins__.TmpDir = ProjectDir + "/tmp"
sys.path.append(LibDir) 

from General import *
from Sequence import *
from Utility import *
from System import *


# General libs
import Image
import array
import imp
import struct
import zlib
import fcntl, struct
import thread
import signal #for CTRL-C

#==========================================
def thread_logRAM(PlotTitle, SleepSeconds):
#==========================================
    #USAGE:
    # logRAM_Thread = threading.Thread(target=thread_logRAM, args=(PlotTitle,))
    # logRAM_Thread.daemon = True
    # logRAM_Thread.start()
        
    #NOTE: main file must call this, otherwise ugly (harmless) error at end of script
    #Importing here will NOT help
#     import matplotlib # forcing to use Agg backend!
#     matplotlib.use('Agg')
#     import matplotlib.pyplot as plt
        
    import copy
    import subprocess
    import threading

        
    KBytesRAM = []
    KBytesSWAP = []
    MaxKBytesRAM = 0
    print PlotTitle

    while 1:
        #-------------------------------------
        # FIND CURRENT RAM STATE 
        #-------------------------------------
        Call = "LANGUAGE=en_US free"
        process = subprocess.Popen(Call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        stdout, stderr = process.communicate()
        #print stdout
        
        SampleRAM = float(re.search(r'cache:\s*(\d*)\s*(\d*)', stdout).group(1))
        SampleSWAP = float(re.search(r'Swap:\s*\d*\s*(\d*)', stdout).group(1))
        MaxKBytesRAM = float(re.search(r'Mem:\s*(\d*)', stdout).group(1))
        
        KBytesRAM.append(SampleRAM)
        KBytesSWAP.append(SampleSWAP)
        print "\nthread_logRAM: MB RAM used: %0.0f" % (SampleRAM/1024)     
        
        #-------------------------------------
        # PLOT CURRENT RAM STATE
        #-------------------------------------
        #plt.hold(False)
        
        fig = plt.figure() 
        fig.suptitle(PlotTitle)  
         
        KBytesRAM_copy = copy.deepcopy(KBytesRAM) # make a copy to freeze number of elements (thread!)
        NumSamples = len(KBytesRAM_copy)
        t = np.arange(0.0, NumSamples/2.0, 0.5)
        constline = np.empty(NumSamples); constline.fill(MaxKBytesRAM)
         
        Sub1 = fig.add_subplot(211)
        Sub1.plot(t, KBytesRAM_copy)
        Sub1.plot(t, constline) #installed RAM
 
        KBytesSWAP_copy = copy.deepcopy(KBytesSWAP) # make a copy to freeze number of elements (thread!)
        NumSamples = len(KBytesSWAP_copy)
        t = np.arange(0.0, NumSamples/2.0, 0.5)
 
        Sub2 = fig.add_subplot(212)
        Sub2.plot(t, KBytesSWAP_copy)
         
        #fig.show() #will not work with Agg backend
        fig.savefig(res("~/Desktop/%s.png" %(PlotTitle)))
        plt.close() 
        plt.clf() 
        
        #-------------------------------------
        # SLEEP 
        #-------------------------------------
        time.sleep(SleepSeconds)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class CMain():
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    
    #==========================================
    def __init__(self):
    #==========================================
        pass
    
    #==========================================
    def run(self):
    #==========================================
        pass

        PlotTitle = "RAM Log"
        SleepSeconds = 10
        logRAM_Thread = threading.Thread(target=thread_logRAM, args=(PlotTitle,SleepSeconds))
        logRAM_Thread.daemon = False
        logRAM_Thread.start()
    
#==========================================
if __name__ == '__main__':
#==========================================
    
    def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    Main = CMain()
    Main.run()
    

    

    




    
