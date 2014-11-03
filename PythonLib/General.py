#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

# # ONLY FOR "A_" SCRIPTS
# import sys, os
# __builtins__.ProjectDir = os.path.abspath("../")
# assert( "HARP" in os.path.basename(ProjectDir) )
# __builtins__.LibDir = ProjectDir + "/PythonLib"
# __builtins__.TmpDir = ProjectDir + "/tmp"
# sys.path.append(LibDir) 

from Imports_Basic import *
from System import *

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class ClassTemplate(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #==========================================
    def __init__(self):
    #==========================================
        super(ClassTemplate, self).__init__()
        # CHANGE HERE -------------------------------------------------
        # -------------------------------------------------------------
        class CAnyClass:
            pass
    #==========================================
    def run(self):
    #==========================================
        #-------------------------------------
        # COMMENT
        #-------------------------------------
        pass
#==========================================
if __name__ == '__main__':
#==========================================    
    #sys.exit(0)
    MyClassTemplate = ClassTemplate()
    MyClassTemplate.run()

        
#==========================================
# GLOBALS
#==========================================
doInvert = True
FigNum = 0


#==========================================
# READING AND WRITING GLOBALS
#==========================================
globvar = 0
def set_globvar_to_one():
    global globvar    # Needed to modify global copy of globvar
    globvar = 1

def print_globvar():
    print globvar     # No need for global declaration to read value of globvar

#==========================================
# FOR LOOP OVER RANGE / LIST
#==========================================
# for By in range(0,NumBlksY):
# for Sequ in self.SequList: 

# #==========================================
# def getEssentialDirs(FileLOC, RelPathToHARP):
# #==========================================
#     HARPDir = os.path.abspath(os.path.dirname(os.path.abspath(FileLOC)) + RelPathToHARP)
#     assert("HARP" in HARPDir), "Not HARP dir: HARPDir"
#     TmpDir = HARPDir + "/tmp"
#     return (HARPDir, TmpDir)

#==========================================
def enum(*sequential, **named):
#==========================================
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Idx1 = enum('NAME', 'ENCBIN', 'DECBIN', 'INI', 'PSNR', 'OVERRIDE', 'INFOSTR')

#==========================================
def assertToolsExist(Tools):
#==========================================
    for Tool in Tools:
        assert os.system(Tool + " --help > /dev/null") == 0, Tool + " not found"

#==========================================
def forceRunInScreen():
#==========================================
    #we check if we run inside screen
    try:
        STY = str(os.environ['STY'])
    except:
        STY = "" 
    assert STY != "", "NOT RUNNING IN SCREEN."
    

 
#==========================================
def assertCMakeVersion_2_8():
#==========================================
    CMakeVersion = os.popen('cmake --version').read()
    assert ("2.8" in CMakeVersion), "CMake version not 2.8, but: " + CMakeVersion
 

#==========================================
def printLARGE(Headline, depth=0, out=sys.stdout):
#==========================================
    if depth == 0:
        Nums, Symbol, Color = (60, "=", cmdcolor.On_Yellow)
    elif depth == 1:
        Nums, Symbol, Color = (60, "=", cmdcolor.On_Green)
    elif depth == 2:
        Nums, Symbol, Color = (40, "=", cmdcolor.BGreen)
    elif depth == 3:
        Nums, Symbol, Color = (30, "-", cmdcolor.IGreen)
    else: 
        Nums, Symbol, Color = (20, "-", cmdcolor.BBlack)
        
    Color = cmdcolor.BBlack #we seem to have problems with colored background

    Headline = Headline + " " * (Nums - len(Headline))
    Line = "\n" + Symbol*Nums + "\n" + Headline + "\n" + Symbol*Nums + "\n"
    print str(Color + Line + cmdcolor.End)
    
#==========================================
def printHistory():
#==========================================
    import readline
    for i in range(readline.get_current_history_length()):
        print readline.get_history_item(i)

#==========================================
def assertDirExists(Path, ErrStr=""):
#==========================================   
    assert os.path.isdir(Path), ErrStr + ": " + Path
    
#==========================================
def assertFileExists(FN, ErrStr=""):
#==========================================   
    assert os.path.isfile(FN), "%s: %s (CWD: %s)" % (ErrStr, FN, getCWD())

#==========================================
def load_INI(FN):
#==========================================      
    assertFileExists(FN, "Missing Pickle File")
    Config = ConfigParser.ConfigParser(allow_no_value=True) # allow keys without values
    Config.optionxform = str #preserve upper/lower case
    LinesRead = Config.read(FN)
    assert (len(LinesRead) == 1)
    return Config
    # then access by self.Config.get(Section, Arg)



#==========================================
def savePickleFN(Object, FN):
#==========================================
    pickle.dump( Object, open(FN, "wb" ), protocol=2 )
    print "PICKLE saved: " + FN
    
#==========================================
def loadPickleFN(FN):
#==========================================
    assertFileExists(FN, "Missing Pickle File")
    return pickle.load(open(FN, "rb" ) )   
    print "PICKLE loaded: " + FN
 
#==========================================   
def analyzePickleFN(FN, ID):
#==========================================
    import GraphViz
    NameRootNode = ID
    Dict   = loadPickleFN(FN)
    prettyprint(Dict, ID, "%s.txt" % ID)
    GraphViz.draw_Dict(Dict, ID,  "%s.png" % ID)

#==========================================
def savePickleFN_Compressed(Object, FN):
#==========================================
    print "Saving compressed PKL... ",
    pklz = gzip.GzipFile(FN, 'wb')
    pklz.write(pickle.dumps(Object, protocol=0))
    pklz.close()
    print "done"
    
#==========================================
def loadPickleFN_Compressed(FN):
#==========================================
    pklz = gzip.GzipFile(FN, 'rb')

    Buffer = ""
    while True:
        data = pklz.read()
        if data == "":
            break
        Buffer += data
    Object = pickle.loads(Buffer)
    pklz.close()
    return Object
 
#==========================================
def prettyprint(Object, ID, FN_out=None): #or any object
#==========================================
    
    import pprint
    print "print_Dict: printing " + ID 
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(Object)
    if (FN_out != None):
        with open(FN_out, 'wt') as out:
            pprint.pprint(Object, stream=out)
    print "print_Dict: done\n"
    return "%s:\n" % ID + pprint.pformat(Object) #to string, too

#==========================================
def warning(Text):
#==========================================
    print cmdcolor.BRed + "WARNING: " + Text + cmdcolor.End
    #print colored('hello', 'red'), colored('world', 'green')
        
#==========================================
def getCommaStringFromList(List):
#==========================================    
    return (','.join(str(i) for i in List))
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class CLock:
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #==========================================
    def __init__(self, FN):
    #==========================================
        self.FN = FN
        self.handle = open(FN, 'w') #create it if it does not exist

    #==========================================
    def acquire(self):
    #==========================================
        #print "Locking..."
        lockdata = struct.pack('hhllhh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
        fcntl.fcntl(self.handle.fileno(),fcntl.F_SETLKW, lockdata)
      
    #==========================================  
    def release(self):
    #==========================================
        fcntl.lockf(self.handle.fileno(), fcntl.LOCK_UN)        

    #==========================================
    def __del__(self):
    #==========================================
        self.handle.close()

#==========================================
# COLORS (OPENCV USES BGR)
#==========================================
#as numpy arrays for easy flipping

WHITE       = [255, 255, 255]
GRAY        = [127, 127, 127]
DARKGRAY    = [64, 64, 64]
BLACK       = [0, 0, 0]
GREEN       = [0, 255, 0]
DARKGREEN   = [0, 64, 0]
YELLOW      = [0, 255, 255]
RED         = [0, 0, 255]
DARKRED     = [0, 0, 64]
BLUE        = [255, 0, 0]
DARKBLUE    = [64, 0, 0]
GREEN_RGB = GREEN[::-1]
BLUE_RGB  = BLUE[::-1]
RED_RGB   = RED[::-1]



# BRBA_YELLOW = (250,201,13)
# BRBA_BLUE   = (44,189,194)
# BRBA_RED    = (220,97,97)
# BRBA_GREEN  = (125,168,168) #7D A8 A8
# 


#define BRBA_YELLOW Scalar(13,201,250)
#define BRBA_BLUE Scalar(194,189,44)
#define BRBA_RED Scalar(52,97,220)
#define BRBA_GREEN Scalar(63,168,125)

#BGR
# GREEN = (0,255,0)
# DARKGREEN = (0,50,0)
# BLUE = (255,0,0)
# DARKBLUE = (50,0,0)
# RED = (0,0,255)
# DARKRED = (0,0,50)
# BRBA_YELLOW = (13,201,250)

#==========================================
# SHELL COLORS
#==========================================
class cmdcolor: 
    
    # Regular Colors
    Black='\033[0;30m'        # Black
    Red='\033[0;31m'          # Red
    Green='\033[0;32m'        # Green
    Yellow='\033[0;33m'       # Yellow
    Blue='\033[0;34m'         # Blue
    Purple='\033[0;35m'       # Purple
    Cyan='\033[0;36m'         # Cyan
    White='\033[0;37m'        # White
    
    # Bold
    BBlack='\033[1;30m'       # Black
    BRed='\033[1;31m'         # Red
    BGreen='\033[1;32m'       # Green
    BYellow='\033[1;33m'      # Yellow
    BBlue='\033[1;34m'        # Blue
    BPurple='\033[1;35m'      # Purple
    BCyan='\033[1;36m'        # Cyan
    BWhite='\033[1;37m'       # White
    
    # Underline
    UBlack='\033[4;30m'       # Black
    URed='\033[4;31m'         # Red
    UGreen='\033[4;32m'       # Green
    UYellow='\033[4;33m'      # Yellow
    UBlue='\033[4;34m'        # Blue
    UPurple='\033[4;35m'      # Purple
    UCyan='\033[4;36m'        # Cyan
    UWhite='\033[4;37m'       # White
    
    # Background
    On_Black='\033[40m'       # Black
    On_Red='\033[41m'         # Red
    On_Green='\033[42m'       # Green
    On_Yellow='\033[43m'      # Yellow
    On_Blue='\033[44m'        # Blue
    On_Purple='\033[45m'      # Purple
    On_Cyan='\033[46m'        # Cyan
    On_White='\033[47m'       # White
    
    # High Intensity
    IBlack='\033[0;90m'       # Black
    IRed='\033[0;91m'         # Red
    IGreen='\033[0;92m'       # Green
    IYellow='\033[0;93m'      # Yellow
    IBlue='\033[0;94m'        # Blue
    IPurple='\033[0;95m'      # Purple
    ICyan='\033[0;96m'        # Cyan
    IWhite='\033[0;97m'       # White

    End = '\033[0m'
