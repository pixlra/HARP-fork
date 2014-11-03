#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *


#==========================================
def initPrintOptions():
#==========================================
    np.set_printoptions(precision = 6)
    np.set_printoptions(linewidth = 120)
    np.set_printoptions(suppress=True)
    
#==========================================
def changeFromTo(FromDir, ToDir):
#==========================================
    FromDir = os.path.dirname(os.path.realpath(FromDir))
    assertDirExists(FromDir)
    os.chdir(FromDir)
    print "Previous working dir: " + os.getcwd()
    assertDirExists(ToDir)
    os.chdir(ToDir)
    print "Current working dir: " + os.getcwd()
    print "Successfully changed to " + os.getcwd()
    
#==========================================
def res(Dir):
#==========================================
    return os.path.expandvars(os.path.expanduser(Dir))

#==========================================
def getUser():
#==========================================
    import getpass
    return getpass.getuser()

#==========================================
def getCWD():
#==========================================
    return os.getcwd()

#==========================================
def getLinesFromFile(FN):
#==========================================
    with open(FN) as f:
        Lines = f.read().splitlines() #splitlines: also remove "\n"
    return Lines

#==========================================
def replaceInFile(FileName, SearchFor, ReplaceWith):
#==========================================
    for line in fileinput.input(FileName, inplace=True): #WARNING: will delete the orig file!
        line = re.sub(SearchFor, ReplaceWith, line)
        print "%s" % (line),  #Back to file
        
#==========================================
def setEnvironmentVar(VarName, Content):
#==========================================    
    if not os.getenv( VarName ):
        os.environ[VarName] = res(Content) 
    else:        
        os.environ[VarName] = res(Content) + ":" + os.environ[VarName]
    
#==========================================
def askUser():
#==========================================  
    print "Is this ok? yes/no"
    yes = set(['yes','y', ''])
    no = set(['no','n'])

    choice = raw_input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        return askUser()
    
#==========================================
def deleteDir(DirName):
#========================================== 
    if os.path.exists(DirName):
        print "WARNING: deleting " + DirName
        #askUser()
        shutil.rmtree(DirName)
        
#==========================================
def createDir(DirName):
#==========================================         
    if not os.path.exists(DirName):
        os.makedirs(DirName)   
        
#==========================================
def copyDir(SrcDir, DstDir):
#==========================================          
    #shutil.copytree(SrcDir, DstDir)  #crap, will throw error on existing Dst
    distutils.dir_util.copy_tree(SrcDir, DstDir)
   
#==========================================
def writeStringToFN(Text, FN):
#==========================================   
    with open(FN, "w") as text_file:
        text_file.write(Text)
        
#==========================================
def logText(Text, FN):
#==========================================
    with open(FN, "a+") as text_file:
        text_file.write(Text + "\n")
    
#==========================================
def splitPathFN(PathFN): 
#==========================================
    Dir, FN = os.path.split(PathFN)
    BN = os.path.splitext(FN)[0]
    DIRBN = Dir + "/" + BN
#     print "Splitting path " + AbsPath
#     print "Extracted FN: " + FN 
#     print "Extracted BN: " + BN
    return (FN, BN, Dir, DIRBN, PathFN)

#==========================================
def getAbsPath(RelativePath): 
#==========================================
    return os.path.abspath(RelativePath)

#==========================================
def flush():
#==========================================
    sys.stdout.flush()  
    
#==========================================
def runCall(Call):
#==========================================
        print "Running: \n" + Call
        assert os.system(Call) == 0, "Call returned error:" + Call 
#         process = subprocess.Popen(Call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
#         for line in iter(process.stdout.readline, b''):
#             sys.stdout.write(line)


            
