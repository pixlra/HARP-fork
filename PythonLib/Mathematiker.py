#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import threading 
import Queue 
import time
import multiprocessing
import traceback
import sys

# HOW A MATHEMATIKER WORKS ================
# The MATHEMATIKER waits for a JOB in the mailbox 
# The JOB contains what he/she should do, along with the right TOOLSET (a blackbox)
# The TOOLSET offers prepare() and apply() functions, which need to know about the MATHEMATIKER's PASSPORT
# The PASSPORT is used to create unique (output) directories while the JOB is done
# The RESULT is returned by Job.Toolset.apply() and written by MATHEMATIKER to a mutex-locked file 
#==========================================

#==========================================
def wakeupMathematiker(NumMathematiker="Auto"): 
#==========================================
    NumMathematiker = multiprocessing.cpu_count() if NumMathematiker == "Auto" else NumMathematiker
    MathematikerList = [Mathematiker() for i in range(NumMathematiker)]
    for ID, aMathematiker in enumerate(MathematikerList): 
        aMathematiker.setDaemon(True)
        aMathematiker.ID = ID
        aMathematiker.start() # heyho single-threaded Mathematiker, start thinking!
            
    print "Mathematiker: wokeup %d Mathematiker, now waiting for jobs" % NumMathematiker
    return MathematikerList #not needed anymore

#====================================================================================
class Mathematiker(threading.Thread): 
#====================================================================================
    
    ThreadLock = threading.Lock() 
    Briefkasten = Queue.Queue() 
     
#     #==========================================
#     def __init__(self):
#     #==========================================
        
    #==========================================
    def run(self): 
    #==========================================
      
        #-------------------------------------
        # WAKING UP
        #-------------------------------------    
        time.sleep(0.1)
        Mathematiker.ThreadLock.acquire() 
        print "Mathematiker %d woke up in his office, waits for work" % self.ID
        Mathematiker.ThreadLock.release() 
    
        while True: 
            #try:            
                #-------------------------------------
                # GET A JOB, DUDE
                #-------------------------------------    
                Toolbox = Mathematiker.Briefkasten.get()  
                print "Mathematiker took job from Mailbox, jobs left: %d" % Mathematiker.Briefkasten.qsize()
                Toolbox.prepare(self.ID) # do some initial setup with the information so far
                
                #-------------------------------------
                # MATHEMATIKER! THINK! APPLY TOOLSET ! HEUREKA!
                #-------------------------------------    
                Toolbox.run();
     
                #-------------------------------------
                # FINISH UP
                #------------------------------------- 
                print str(Mathematiker.Briefkasten.qsize()) + " jobs still waiting in mailbox ..."
                Mathematiker.ThreadLock.acquire() #thread safe file IO
#                 ResultsFile = open(Toolset.ResultsFile, "a")
#                 ResultsFile.write(Result)
#                 ResultsFile.close()
                Mathematiker.ThreadLock.release() 
                Mathematiker.Briefkasten.task_done() 

# USE THIS CODE IF MATHEMATIKER CRASHES AND NEEDS REHAB
#             except Exception, Str:
#                 print "EXCEPTION------------------------"
#                 print "Unexpected ERROR:", sys.exc_info()[0]
#                 traceback.print_tb(sys.exc_info()[2])
#                 print Str  
#                 print "---------------------------------"
#                 Mathematiker.Briefkasten.task_done()  #prevent thread lock in case of exception
#                 raise
