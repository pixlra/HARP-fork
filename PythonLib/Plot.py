#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *

import Image
import getpass

# import matplotlib.mlab as mlab
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# 
# 
# from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=True)

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PyQt4'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pylab

from Qt import *

from General import *
from Warp import *

#==========================================
def plot_ImgBGR(Img, title="", cmap='gray', Block=False):
#==========================================
    RGB = cv2.cvtColor(Img, cv2.COLOR_BGR2RGB)
    plot_Img(RGB, title=title, cmap=cmap, Block=Block)

#==========================================
def plot_Img(Img, title="", cmap='gray', Block=False):
#==========================================
    if doInvert:
        Img = invertImage(Img)
        
    #plt.close()
    Size = 1.0/1.2
    fig = plt.figure(1, figsize=(22*Size,11.9*Size))
    fig.clf() # fix memory leak of figure already open
    #fig = plt.figure(1)
    
    plt.imshow(Img) #,vmin=0,vmax=255)
    plt.title(title)
    plt.axis('off')

    if len(Img.shape) == 2: # luminance channel
        CMap = pylab.gray()
        plt.colorbar(CMap)
        
    plt.tight_layout()
    plt.show(block=Block)
    plt.pause(0.001) 
    
#     fig.clf()
#     plt.close()
    
    
# EXAMPLE:
# fig = plt.figure(figsize=(22,11.9))
# plt.subplot(3, 3, 1) 
# subplot_Img(Img, "Img")
# plt.show()
#==========================================
def subplot_Img(Img, cmap='gray', scale=False):
#==========================================
    if doInvert:
        Img = invertImage(Img)

    if scale is True: #let matplotlib decide the dynamic range
        plt.imshow(Img, cmap=pylab.gray())
    else: 
        plt.imshow(Img, cmap=pylab.gray(), vmin=0, vmax=255)
    plt.axis('off')
    
    
    #plt.set_cmap(cmap)
    #Fig = plt.figure()
    #
    #plt.colorbar()
    #Fig.delaxes(Fig.axes[1])  #removes colorbar 
    
# EXAMPLE:
# fig = plt.figure(figsize=(22,11.9))
# fig.canvas.set_window_title(Sequ.FN)
# plt.subplot(5, 1, 1) 
# plt.subplots_adjust(hspace = 0.5)
# subplot_Bar(TS_POCs, BGS_Ducati.TS_SkipPercentage, "BGS_Ducati.TS_SkipPercentage", (1, Sequ.Fr))
#==========================================
def subplot_Bar(x, y, title, xlimits):
#==========================================
    # we need xlimits, otherwise leading/trailing zero elements are not shown
    plt.bar(x, y)
    plt.xlim(xlimits[0], xlimits[1])
    plt.title(title)


#==========================================
def plot_Sankey():
#==========================================
    from matplotlib.sankey import Sankey
    s = 1
    Sankey(flows=[100/s, -15/s, -5/s, -80/s],
           labels=["", "","",""],
           #labels=['Input', 'Rotation', 'Zoom','Translational/\nStill'],
           orientations=[ 0, 1, 1, 0],
           scale=0.01,
           format='%.0f', unit='%', 
           #offset=20,
           pathlengths = [2, 1-0.5, 1.2-0.5, 1],
           head_angle=90,
           lw=2.0
            ).finish()
    plt.title("The default settings produce a diagram like this.")
    plt.savefig("tmp/SankeyArrow.svg" )
    plt.show()
    
#==========================================
def plot_Warping(Ref, Cur, H, Title=""):  #FigNum
#==========================================

    Fig = plt.figure(figsize=(22,11.9))
    
    Fig.suptitle(Title, fontsize=20)
    
    plt.subplot(1, 4, 1)
    subplot_Img(Ref[:,:,0], "Ref")

    plt.subplot(1, 4, 2)
    subplot_Img(Cur[:,:,0], "Cur")
    
    plt.subplot(1, 4, 3)
    subplot_Img(getLumDiff(Ref, Cur), "LumDiff Ref - Cur", scale=True)
    
    plt.subplot(1, 4, 4)
    subplot_Img(getWrpdLumDiff(Ref, Cur, H), "LumDiff WRPD_Ref - Cur", scale=True)
    
    return Fig

#==========================================
def plot_ImageRow(ImgRow, Title="", SubTitles=[]): #FigNum, 
#==========================================

    Fig = plt.figure()#plt.figure(figsize=(22,11.9))
    
    Fig.suptitle(Title, fontsize=20)
    
    NumImages = len(ImgRow)
    
    for Idx, Img in enumerate(ImgRow):
    
        ax = plt.subplot(1, NumImages, Idx+1) #prepare subplot
        subplot_Img(Img, scale=False)
        SubTitle = SubTitles[Idx] if len(SubTitles) > Idx else ""
        ax.set_title(SubTitle)


    return Fig

#==========================================
def subplot_EXAMPLE():
#==========================================
    fig = plt.figure()
    # Example data
    Performer = ('Performer0', 'Performer1', 'Performer2', 'Performer3', 'Performer4')
    x_pos = np.arange(len(Performer))
    #how each performer performs in catgory X, one entry for each performer
    Cat0_Performance = 3 + 10 * np.random.rand(len(Performer))  
    Cat1_Performance = 3 + 10 * np.random.rand(len(Performer))
    Cat2_Performance = 3 + 10 * np.random.rand(len(Performer))
    
    Cat0_Label, Cat0_Color = "Translations", 'r'
    Cat1_Label, Cat1_Color = "Rotations", 'g'
    Cat2_Label, Cat2_Color = "Zooms", 'b'
    
    
    width = 0.15
    #think of only the leftmost bar-collection (first "Group")
    #all other groups 
    plt.bar(x_pos+0*width, Cat0_Performance, width, color=Cat0_Color)
    plt.bar(x_pos+1*width, Cat1_Performance, width, color=Cat1_Color)  
    plt.bar(x_pos+2*width, Cat2_Performance, width, color=Cat2_Color,)
    plt.xticks(x_pos+1.5*width, Performer)
    #plt.title('How fast do you want to go today?')
    
    plt.axhline(y=Cat0_Performance[0], linewidth=2, xmin=0.0, linestyle="--", color=Cat0_Color)
    plt.axhline(y=Cat1_Performance[0], linewidth=2, xmin=0.01*3.5, linestyle="--", color=Cat1_Color)
    plt.axhline(y=Cat2_Performance[0], linewidth=2, xmin=0.02*3.5, linestyle="--", color=Cat2_Color)
    
    #pyplot.hlines(Cat0_Performance[0], 0, x_arr, color='red')
    plt.legend((Cat0_Label, Cat1_Label, Cat2_Label))
    
    plt.show()
#====================================================================================
# SPECIAL
#====================================================================================

#==========================================
def plotFigure_MotionClassifierPerf(ClassifierNames, CategoryNames, CategoryPerformance, EpsFN):
#==========================================
    
    global FigNum
    fig = plt.figure(FigNum, figsize=(6.2, 5.5), dpi=80)
    FigNum = FigNum + 1
    
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 12})
    plt.subplots_adjust(left=0.11, right=0.97, top=0.94, bottom=0.11)
    
    width = 0.25
    #offs = len(CategoryNames)/3*width
    
    # Example data
    Performer = ClassifierNames
    x_pos = np.arange(len(Performer))
    #how each performer performs in catgory X, one entry for each performer
    Cat0_Performance = CategoryPerformance[0]  
    Cat1_Performance = CategoryPerformance[1] 
    Cat2_Performance = CategoryPerformance[2] 
    
    Cat0_Label, Cat0_Color = CategoryNames[0], 'r'
    Cat1_Label, Cat1_Color = CategoryNames[1], 'g'
    Cat2_Label, Cat2_Color = CategoryNames[2], 'b'
    
    #think of only the leftmost bar-collection (first "Group")
    #all other groups 
    plt.bar(x_pos+0*width, Cat0_Performance, width, color=Cat0_Color)
    plt.bar(x_pos+1*width, Cat1_Performance, width, color=Cat1_Color)
    plt.bar(x_pos+2*width, Cat2_Performance, width, color=Cat2_Color)
    plt.xticks(x_pos+1.5*width, Performer)
    #plt.title('How fast do you want to go today?')
    ax = fig.gca() 
    ax.set_ylabel('Number of frames')

    plt.legend((Cat0_Label, Cat1_Label, Cat2_Label), loc='center left')
    
    plt.axhline(y=Cat0_Performance[0], linewidth=2, xmin=0.0, linestyle="--", color=Cat0_Color)
    plt.axhline(y=Cat1_Performance[0], linewidth=2, xmin=0.01*4.0, linestyle="--", color=Cat1_Color)

    plt.axhline(y=Cat2_Performance[0], linewidth=2, xmin=0.02*4.3, linestyle="--", color=Cat2_Color)
    
    #-------------------------------------
    # EXPORT FIGURE 1
    #-------------------------------------    
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
    #plt.savefig("%s1.png" % DIRBN) #not used
    plt.savefig("%s.svg" % DIRBN)
    #os.system("inkscape --export-eps=%s1.eps %s.svg" % (DIRBN, DIRBN))
    
    #plt.ylim(0, 600)
    #ax.set_ylim(-20, 20)
    
#==========================================
def plotFigure_NaturalSequences_ZoomRotValues(FE):
#==========================================
    FS = 12 #font size
    fig = plt.figure(1, figsize=(3.5, 6), dpi=80)
    ax = fig.gca()
    
    ax = fig.gca() 
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': FS})
    plt.subplots_adjust(left=0.18, right=0.78, top=0.95, bottom=0.10)

    
    x = np.arange(1,FE.shape[0]/2)
    ax.plot(x, FE[200:400,ROTVAL_GT], label="GT angle", c='g')
    ax.plot(x, FE[200:400,ROTVAL], label="Estim. angle", c='r')
    ax.set_xlabel('Frame index')
    ax.set_ylim(-0.2, 0.30)
    ax.set_ylabel('Rotation angle (in deg)', color='g', fontsize=FS)
    for tl in ax.get_yticklabels():
        tl.set_color('g')
    ax.legend(loc='upper left', title=r"Sequ. Spincalendar", fontsize=FS)
    #legend = ax.legend( shadow=False, numpoints=1, loc='upper left') #loc='upper center',
    #legend.get_frame().set_facecolor('0.90')    
    
    #fig = plt.figure(2)
    ax2 = ax.twinx()
    #ax2 = fig.gca()
    ax2.plot(x, FE[:198,RATIOVAL_GT], label="GT zoom", c='b')
    ax2.plot(x, FE[:198,RATIOVAL], label="Estim. zoom", c='y')
    ax2.set_ylim(0.99, 1.01)
    ax2.set_ylabel('Zoom (scale factor)', color='b', fontsize=FS)
    for tl in ax2.get_yticklabels():
        tl.set_color('b')
    ax2.legend(loc='lower right', title=r"Sequ. Bigships", fontsize=FS)
    #plt.tight_layout()
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN('tmp/Figure_NaturalSequences_RotZoomValues.eps')
    plt.savefig("%s.svg" % DIRBN)   
    
    
#==========================================
def plotFigure_NaturalSequences_MoClaPerformance(ClassifierNames, CategoryNames, CategoryPerformance, EpsFN):
#==========================================
    
    global FigNum
    fig = plt.figure(FigNum, figsize=(3.5, 6), dpi=80)
    FigNum = FigNum + 1
    
    FS = 12 #font size
    
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 12})
    plt.subplots_adjust(left=0.18, right=0.97, top=0.94, bottom=0.11)
    
    width = 0.25
    #offs = len(CategoryNames)/3*width
    
    # Example data
    Performer = ClassifierNames
    x_pos = np.arange(len(Performer))
    ax = fig.gca() 
    ax.set_ylabel('Number of frames')
    #how each performer performs in catgory X, one entry for each performer
    Cat0_Performance = CategoryPerformance[0]  
    Cat1_Performance = CategoryPerformance[1] 
    Cat2_Performance = CategoryPerformance[2] 
    
    Cat0_Label, Cat0_Color = CategoryNames[0], 'r'
    Cat1_Label, Cat1_Color = CategoryNames[1], 'g'
    Cat2_Label, Cat2_Color = CategoryNames[2], 'b'
    
    #think of only the leftmost bar-collection (first "Group")
    #all other groups 
    plt.bar(x_pos+0*width, Cat0_Performance, width, color=Cat0_Color)
    plt.bar(x_pos+1*width, Cat1_Performance, width, color=Cat1_Color)
    plt.bar(x_pos+2*width, Cat2_Performance, width, color=Cat2_Color)
    plt.xticks(x_pos+2*width, Performer)
    #plt.title('How fast do you want to go today?')
    

    plt.legend((Cat0_Label, Cat1_Label, Cat2_Label), loc='upper left', fontsize=FS)
    
    plt.axhline(y=Cat0_Performance[0], linewidth=2, xmin=0.0, linestyle="--", color=Cat0_Color)
    plt.axhline(y=Cat1_Performance[0], linewidth=2, xmin=0.02*4.7, linestyle="--", color=Cat1_Color)

    plt.axhline(y=Cat2_Performance[0], linewidth=2, xmin=0.04*4.5, linestyle="--", color=Cat2_Color)
    plt.ylim(0, 300)
    #-------------------------------------
    # EXPORT FIGURE 1
    #-------------------------------------    
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
    #plt.savefig("%s1.png" % DIRBN) #not used
    plt.savefig("%s.svg" % DIRBN)
    #os.system("inkscape --export-eps=%s1.eps %s.svg" % (DIRBN, DIRBN))
    
    #plt.ylim(0, 600)
    #ax.set_ylim(-20, 20)

#==========================================
def plotFigure_ClassifierSIFTvsSADvsSSD(ClassifierNames, CategoryNames, CategoryPerformance, EpsFN):
#==========================================
    
    global FigNum
    fig = plt.figure(FigNum, figsize=(7, 4), dpi=80)
    FigNum = FigNum + 1
    
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 12})
    plt.subplots_adjust(left=0.13, right=0.97, top=1.0, bottom=0.13)
    
    width = 0.35
    offs = len(CategoryNames)/2*width
    
    # Example data
    Performer = ClassifierNames
    x_pos = np.arange(len(Performer))
    #how each performer performs in catgory X, one entry for each performer
    Cat0_Performance = CategoryPerformance[0]  
    Cat1_Performance = CategoryPerformance[1] 

    Cat0_Label, Cat0_Color = CategoryNames[0], 'g'
    Cat1_Label, Cat1_Color = CategoryNames[1], 'b'

    #think of only the leftmost bar-collection (first "Group")
    plt.bar(x_pos+0*width, Cat0_Performance, width, color=Cat0_Color)
    plt.bar(x_pos+1*width, Cat1_Performance, width, color=Cat1_Color)

    plt.xticks(x_pos+offs, Performer)


    plt.legend((Cat0_Label, Cat1_Label), loc='upper left', title="Detected motion:")

    plt.axhline(y=Cat0_Performance[0], linewidth=2, xmin=0.0, linestyle="--", color=Cat0_Color)
    plt.axhline(y=Cat1_Performance[0], linewidth=2, xmin=0.01*9, linestyle="--", color=Cat1_Color)

    #-------------------------------------
    # EXPORT FIGURE 1
    #-------------------------------------    
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
    #plt.savefig("%s1.png" % DIRBN) #not used
    plt.savefig("%s.svg" % DIRBN)
    #os.system("inkscape --export-eps=%s1.eps %s1.svg" % (DIRBN, DIRBN))
    
    #plt.ylim(0, 600)
    #ax.set_ylim(-20, 20)
    
#==========================================
def plot3D_Figure_SKIPvsINTERvsXX(Version, AxStr, Data, LA, EpsFN):
#==========================================

    global FigNum
    fig = plt.figure(FigNum, figsize=(6, 4), dpi=80)
    FigNum = FigNum + 1

    #-------------------------------------
    # PLOT BEAUTY
    #-------------------------------------
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 12})
    
    FigTitle = ""    #%s VS. %s VS. %s" % (AxStr[0], AxStr[1], AxStr[2])
    ax = fig.add_subplot(111, projection='3d', title=FigTitle)
        
    #-------------------------------------
    # DATA
    #-------------------------------------
    MRK_SIZE = 9
    ROT_LEGEND = "Rotation"
    ROT_COL = 'g'
    ROT_MRK = '^'
    ax.plot(Data[0][np.where(LA == ROT)], 
               Data[1][np.where(LA == ROT)], 
               Data[2][np.where(LA == ROT)], 
               c=ROT_COL, marker=ROT_MRK, label=ROT_LEGEND, markersize=MRK_SIZE, linestyle='None') 
    
    ZOOM_LEGEND = "Zoom"
    ZOOM_COL = 'b'
    ZOOM_MRK = '^'
    ax.plot(Data[0][np.where(LA == ZOOM)], 
               Data[1][np.where(LA == ZOOM)], 
               Data[2][np.where(LA == ZOOM)], 
               c=ZOOM_COL, marker=ZOOM_MRK, label=ZOOM_LEGEND, markersize=MRK_SIZE, linestyle='None') 
    
    TRST_LEGEND = "Translation"
    TRST_COL = 'r'
    TRST_MRK = '^'
    ax.plot(Data[0][np.where(LA == TRST)], 
               Data[1][np.where(LA == TRST)], 
               Data[2][np.where(LA == TRST)], 
               c=TRST_COL, marker=TRST_MRK, label=TRST_LEGEND, markersize=MRK_SIZE, linestyle='None') 
    
    ax.set_xlabel(AxStr[0])
    ax.set_ylabel(AxStr[1])
    ax.set_zlabel(AxStr[2])
    
    #-------------------------------------
    # PLOT BEAUTY
    #-------------------------------------
#     legend = ax.legend( shadow=False, numpoints=1) #loc='upper center',
#     legend.get_frame().set_facecolor('0.90')
    def my_on_click(event):
        print(ax.elev, ax.azim)
    
    #plt.zticks([0, 1, 2])
    if Version=="Version1":
        plt.subplots_adjust(left=0.00, right=0.96, top=0.99, bottom=0.04)
        LegendLoc = 'upper right'
    
    if Version=="Version2":
        ax.set_zticklabels(["0", "", "1", "", "2"]) 
        plt.subplots_adjust(left=0.03, right=0.96, top=0.99, bottom=0.04)
        LegendLoc = 'upper right'
        
    #-------------------------------------
    # EXPORT FIGURE 1
    #-------------------------------------
    legend = ax.legend( shadow=False, numpoints=1, loc=LegendLoc) #loc='upper center',
    legend.get_frame().set_facecolor('0.90')
    fig.canvas.mpl_connect('button_release_event', my_on_click)
    #ax.view_init(elev=30.4, azim=41.1)
    ax.view_init(elev=28.1, azim=-15.5)
    
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
    #plt.savefig("%s1.png" % DIRBN) #not used
    plt.savefig("%s_left.svg" % DIRBN)
    #os.system("inkscape --export-eps=%s1.eps %s1.svg" % (DIRBN, DIRBN))

#     #-------------------------------------
#     # EXPORT FIGURE 2
#     #-------------------------------------    
#     #legend = ax.legend( shadow=False, numpoints=1, loc='upper right') #loc='upper center',
#     #legend.get_frame().set_facecolor('0.90')
#     fig.canvas.mpl_connect('button_release_event', my_on_click)
#     ax.view_init(elev=30.4, azim=-36.0)
#     
#     (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
#     #plt.savefig("%s2.png" % DIRBN) #not used
#     plt.savefig("%s_right.svg" % DIRBN)
#     #os.system("inkscape --export-eps=%s2.eps %s2.svg" % (DIRBN, DIRBN))
    
#==========================================
def plot2D_Figure_SADvsSSD(AxStr, Data, LA, EpsFN):
#==========================================

    global FigNum
    fig = plt.figure(FigNum, figsize=(6, 4), dpi=80)
    FigNum = FigNum + 1

    #-------------------------------------
    # PLOT BEAUTY
    #-------------------------------------
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 12})
    
    FigTitle = ""    #%s VS. %s VS. %s" % (AxStr[0], AxStr[1], AxStr[2])
    ax = fig.add_subplot(111, title=FigTitle)
    #plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.subplots_adjust(left=0.13, right=0.97, top=0.9, bottom=0.1)
       
        
    #-------------------------------------
    # DATA
    #-------------------------------------
    MRK_SIZE = 8
    

    
    ROT_LEGEND = "Rotation"
    ROT_COL = 'g'
    ROT_MRK = '^'
    ax.plot(Data[0][np.where(LA == ROT)], 
               Data[1][np.where(LA == ROT)], 
               c=ROT_COL, marker=ROT_MRK, label=ROT_LEGEND, markersize=MRK_SIZE, linestyle='None') 
    
    ZOOM_LEGEND = "Zoom"
    ZOOM_COL = 'b'
    ZOOM_MRK = '^'
    ax.plot(Data[0][np.where(LA == ZOOM)], 
               Data[1][np.where(LA == ZOOM)], 
               c=ZOOM_COL, marker=ZOOM_MRK, label=ZOOM_LEGEND, markersize=MRK_SIZE, linestyle='None') 
    
    TRST_LEGEND = "Translation"
    TRST_COL = 'r'
    TRST_MRK = '^'
    ax.plot(Data[0][np.where(LA == TRST)], 
               Data[1][np.where(LA == TRST)], 
               c=TRST_COL, marker=TRST_MRK, label=TRST_LEGEND, markersize=MRK_SIZE, linestyle='None') 

    #plt.subplots_adjust(left=0.13, right=0.97, top=0.9, bottom=0.1)

    
    #-------------------------------------
    # PLOT BEAUTY
    #-------------------------------------
    legend = ax.legend( shadow=False, numpoints=1, loc='upper left') #loc='upper center',
    #legend.get_frame().set_facecolor('0.90')

    ax.annotate("Distinction of motion\n difficult in this\n value range", xy=(19+1,1230+500+50),
            horizontalalignment='center', verticalalignment='center')

    from matplotlib.patches import Ellipse
    el = Ellipse((20,1230), 22, 2100, facecolor='r', alpha=0.5)
    ax.add_artist(el)
    el.set_clip_box(ax.bbox)
    
    ax.set_xlabel(AxStr[0])
    ax.set_ylabel(AxStr[1])
    
#     ax.set_xlim(-20, 20)
#     ax.set_ylim(-20, 20)

    
    #-------------------------------------
    # EXPORT FIGURE 1
    #-------------------------------------    
    (FN, BN, Dir, DIRBN, AbsPath) = splitPathFN(EpsFN)
    #plt.savefig("%s1.png" % DIRBN) #not used
    plt.savefig("%s.svg" % DIRBN)
    #os.system("inkscape --export-eps=%s.eps %s.svg" % (DIRBN, DIRBN))


