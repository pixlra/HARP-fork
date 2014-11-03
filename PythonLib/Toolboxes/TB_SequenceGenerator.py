#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

from Imports_Basic import *
from OpenCV import *
from Warp import *

PRECISION = np.float64

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class SequenceGenerator(object):
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #==========================================
    def __init__(self, SourceImageFN):
    #==========================================
        super(SequenceGenerator, self).__init__()
        assert( "HARP" in os.path.basename(ProjectDir) )
        
        # CHANGE HERE -------------------------------------------------
        self.RescaleWidth=2300
        self.VertOffsetFactor=0.0 #-0.25 #-0.25
        self.FinalSize=(1920, 1080)
        self.WARP_INTERP = cv2.INTER_CUBIC #cv2.INTER_LINEAR cv2.INTER_CUBIC
        self.PRECISION = np.float64
        self.NumFrames = 6
        self.Motion = "roll"   #give some string to describe the chosen parameters of pitch, yaw & roll
        self.showGUI = False
        self.OutputDir = ProjectDir + "/Various/YUVs"
        self.verbose = True
        self.showPlot = False
        # -------------------------------------------------------------

        #-------------------------------------
        # LOAD SOURCE IMAGE
        #-------------------------------------
        self.SourceImageFN = SourceImageFN
        self.loadSourceImage()

        #-------------------------------------
        # OTHER
        #-------------------------------------        
        self.eye = np.eye(3, dtype=PRECISION)
        np.set_printoptions(precision=4)
        np.set_printoptions(suppress=True)
        
    #==========================================
    def get_Ref_and_Cur(self, H_gt, H_accu_last):
    #==========================================
        DimX, DimY = self.DimX, self.DimY
    
        PosS = np.eye(3, dtype=PRECISION)
        Minus = np.eye(3, dtype=PRECISION)
        Minus[0,2] = -1.0;
        Minus[1,2] = -1.0;
         
        # 3 | Global-Image to Search-Image (i.e. final image)
        Warper = CWarper()
        BlockPosX = DimX/2.0 - self.DimXF/2.0;
        BlockPosY = (DimY/2.0 + self.VertOffset) - self.DimYF/2.0; 
        Warper.setBlockPos(BlockPosX, BlockPosY)      
        
        H_crop  = Warper.getTransform_Hgg_to_Hgb(self.eye) #simple cropping, creating final (F) images
        H_bb_gt = Warper.getTransform_Hgg_to_Hbb(H_gt)     #get H which warps Ref_F to Cur_F
        
        # 1 | Need to transform H_gg to H_ss
        #H_ss_gt = np.dot(Minus*PosB, np.dot(H_gt, PosB))
        
        Ref = warpPerspective(self.Orig, H_accu_last, (DimX, DimY), flags=self.WARP_INTERP, borderValue=(0, 128, 128))
        Cur = warpPerspective(Ref, H_gt,        (DimX, DimY), flags=self.WARP_INTERP, borderValue=(0, 128, 128))
        
        # F=Final images
        Ref_F = warpPerspective(Ref, H_crop, (self.DimXF, self.DimYF), flags=self.WARP_INTERP, borderValue=(0, 128, 128))
        Cur_F = warpPerspective(Cur, H_crop, (self.DimXF, self.DimYF), flags=self.WARP_INTERP, borderValue=(0, 128, 128))
        
        H_F = H_bb_gt # since Ref_F and Cur_F are just "blocks": H_bb_gt describes warping from Ref_F to Cur_F 
        return (Ref_F, H_F, Cur_F) 
                    
    #==========================================
    def loadSourceImage(self):
    #==========================================
    
        FN = self.SourceImageFN
        assertFileExists(FN, "Missing Source Image")
        Raw = imread(FN)
        (self.DimXF, self.DimYF)  = self.FinalSize
        
        # NOTE: Raw may be any resolution, so we may want to rescale first
        # NOTE: if its too small, then resize to get rid of black borders
        # NOTE: if its too big, then resize to get an object into focus (Buzz)
        if self.RescaleWidth == None:
            Orig = Raw
        else: 
            RatioX = float(Raw.shape[1])/self.RescaleWidth
            Height = int(np.floor(Raw.shape[0]/RatioX)) /2*2 #  by2times2: make number even
            Orig = cv2.resize(Raw, (self.RescaleWidth, Height), interpolation=cv2.INTER_CUBIC)
            
        (DimY, DimX, Ch) = Orig.shape
        self.VertOffset = DimY * self.VertOffsetFactor
        
        if (self.verbose):
            print "Resolution of original image: %dx%d" % (DimX, DimY)
            print "Type of original image: %s" % Orig.dtype        
        Orig = cv2.cvtColor(Orig, cv2.COLOR_RGB2YUV)
        assert DimX % 2 == 0 and DimY % 2 == 0, "Error: check input image dimensions" #probably not necessary

        self.Orig = Orig
        self.DimX = DimX
        self.DimY = DimY        
        

        

    
    #==========================================
    def create_H_gt(self, pitch, yaw, roll, tx, ty):
    #==========================================
    
        CenterX = self.DimX/2
        CenterY = self.DimY/2
            
        #From degrees to radians
        pitch = pitch*m.pi/180.0
        yaw   = yaw*m.pi/180.0
        roll  = roll*m.pi/180.0
        
        X = np.eye(4, dtype=PRECISION)
        Y = np.eye(4, dtype=PRECISION)
        Z = np.eye(4, dtype=PRECISION)

        sinx, cosx = m.sin(pitch), m.cos(pitch)
        siny, cosy = m.sin(yaw), m.cos(yaw)
        sinz, cosz = m.sin(roll), m.cos(roll)
    
        X[1,1], X[1,2] = cosx, -sinx
        X[2,1], X[2,2] = sinx, cosx        
        Y[0,0], Y[0,2] = cosy, siny
        Y[2,0], Y[2,2] = -siny, cosy
        Z[0,0], Z[0,1] = cosz, -sinz
        Z[1,0], Z[1,1] = sinz, cosz

        H4x4 = np.dot(Z, np.dot(Y, X))
        #Rtest = Z*Y*X; # THIS DOES NOT WORK! THIS IS ELEMENTWISE MULTIPLICATION!
        
        ToCenter = np.eye(4, dtype=PRECISION)
        ToOrigin = np.eye(4, dtype=PRECISION)
        
        ToOrigin[0,3], ToOrigin[1,3] = -CenterX, -CenterY
        ToCenter[0,3], ToCenter[1,3] = CenterX, CenterY;
        
        H4x4_Centered = np.dot(ToCenter, np.dot(H4x4, ToOrigin))
        
        #print "Created H4x4:\n",H4x4
        #print "H4x4_Centered:\n",H4x4_Centered
        
        H3x3 = np.eye(3, dtype=PRECISION) # set all z values to zero (we project to screen plane)
        
        # NOTE THAT H IS FORCED TO AFFINE MODEL
        H3x3[0,0] = H4x4_Centered[0,0];
        H3x3[0,1] = H4x4_Centered[0,1];
        H3x3[0,2] = H4x4_Centered[0,3] + tx;
        H3x3[1,0] = H4x4_Centered[1,0];
        H3x3[1,1] = H4x4_Centered[1,1];
        H3x3[1,2] = H4x4_Centered[1,3] + ty;
        
        #HACK Note that small values have severe impact!
        #H3x3[2,0] = 0.00001;
        #H3x3[2,1] = 0.00001;
        
        #make sure this matrix can be >>perfectly<< written to yml file
        #cv.Save("tmp/tmp.H3x3", cv.fromarray(H3x3))
        #H3x3 = np.asarray(cv.Load("tmp/tmp.H3x3"))
        
        if (self.verbose):
            print "H3x3 (affine enforced):\n",H3x3
        
        return H3x3
    
    #==========================================
    def generateSequence(self):
    #==========================================
        #sys.exit(0)
        
        #-------------------------------------
        # PREPARE OUTPUT DIRS AND FILES
        #-------------------------------------
        # BaseName: will be name of GT directory
        (FN, BN, Dir, DIRBN, PathFN) = splitPathFN(self.SourceImageFN)
        BN = "%s_%dx%d" % (BN, self.DimXF, self.DimYF)
        
        os.system("mkdir -p " + self.OutputDir)
        os.system("mkdir -p " + self.OutputDir + "/%s" % BN)
        
        createDir(self.OutputDir)
        self.FN_YUV = self.OutputDir + "/%s.yuv" % BN
        self.FN_PKL = self.OutputDir + "/%s/%s.pkl" % (BN, BN)

        #-------------------------------------
        # PREPARATION
        #-------------------------------------
        YUV_FileH = open(self.FN_YUV, "wb")
        DimX, DimY = self.DimX, self.DimY
       
        #-------------------------------------
        # MOTION INCREMENTS
        #------------------------------------- 
        pitch = yaw = roll = tx = ty = 0.0;
        tx = ty = 0.0; #WARNING: DO NOT CHANGE! BUG! (TODO, MAYBE H_crop ISSUE?)
        assert(ty == tx == 0.0)
        
        if self.Motion == "pitch":
            pitch = 4.0 #increment
        elif self.Motion == "yaw":
            yaw = 4.0 #increment
        elif self.Motion == "roll":
            roll = 4.0 #increment       
        else: assert 0

        H_accu_last = self.create_H_gt(pitch, yaw, -roll*self.NumFrames/2, tx, ty) #start H is rotated hard to the left
        #H_accu_last = self.create_H_gt(0, 0, 0, 0, 0, DimX/2, DimY/2)
        #H_accu_last= np.eye(3, dtype=PRECISION) #THIS WILL NOT WORK!! CAREFULL WITH TRANSLATION!
        #Ref = Img
        
        POC_Hgt = {}
        
        #==========================================
        # FOR EACH POC
        #==========================================
        for POC in np.arange(0, self.NumFrames, 1):
            print "Processing POC %d" % POC
            
            roll = roll + 2 #make increment grow to have unique warpings 
            
            if POC == 2:
                H_gt = self.create_H_gt(0, 0, 0, 5.0, 0)
            elif POC == 3:
                H_gt = self.create_H_gt(0, 0, 0, -10.25, 0)
            else:
                print "Pitch=%f, Yaw=%f, Roll=%f, tx=%f, ty=%f" % (pitch, yaw, roll, tx, ty)
                H_gt = self.create_H_gt(pitch, yaw, roll, tx, ty)
                
#             print "Pitch=%f, Yaw=%f, Roll=%f, tx=%f, ty=%f" % (pitch, yaw, roll, tx, ty)
#             H_gt = self.create_H_gt(pitch, yaw, roll, tx, ty, DimX/2, DimY/2)
            
            (Ref_F, H_F, Cur_F) = self.get_Ref_and_Cur(H_gt, H_accu_last)
            
            if self.showPlot:
                Diff = getWrpdLumDiff(Ref_F, Cur_F, H_F)
                cv2.imshow('Diff', Diff)
                cv2.waitKey()
            
            write_YUV(YUV_FileH, Cur_F)
            POC_Hgt[POC] = H_F
            
            
            
#             os.system("mkdir -p tmp")
#             cv2.imwrite("./tmp/Ref.png", Ref)
#             cv2.imwrite("./tmp/Cur.png", Cur)
                
            #-------------------------------------
            # LAST BE FIRST
            #-------------------------------------
            H_accu_last = np.dot(H_gt, H_accu_last)
            
            # for testing
            Last_Ref_F = Ref_F
            Last_H_bb_gt = H_F
            
        #write pickle

        savePickleFN(POC_Hgt, self.FN_PKL )
    
    #==========================================
    def ECC_Testbench(self, RefOrig, CurOrig, H_gg_gt):
    #==========================================

        if self.doEvaluatePrecision == False:
            return

        #sys.exit(0)
        D = 32 #Block dimension
        eye = np.eye(3, dtype=PRECISION)
        
        Ref = RefOrig[:,:,0];
        Cur = CurOrig[:,:,0];
#         Ref = cv2.cvtColor(np.copy(RefOrig), cv2.COLOR_YUV2GRAY_IYUV)
#         Cur = cv2.cvtColor(np.copy(CurOrig), cv2.COLOR_YUV2GRAY_IYUV)
        
        DimX = self.DimX_Master
        DimY = self.DimY_Master
    
        #----------------------------------
        # other
        #----------------------------------
        os.system("mkdir -p tmp")
        imwrite("tmp/Ref.png", Ref)
        imwrite("tmp/Cur.png", Cur)
        Ref_wrpd_collection = np.zeros(Ref.shape, np.uint8)*128

        #----------------------------------
        # Running optical flow to get Init-H for ECC
        #----------------------------------
        print "Calculating optical flow..."
        assert not os.system("C++/tvl1_optical_flow " + " tmp/Ref.png tmp/Cur.png " + " tmp/OpticalFlow.yml")
        Flow = np.asarray(cv.Load("tmp/OpticalFlow.yml"))
        ygrid, xgrid = np.mgrid[0:DimY,0:DimX].reshape(2,-1)
        fx, fy = Flow[ygrid, xgrid].T
        pt0 = PRECISION(np.vstack([xgrid, ygrid]).T)
        pt1 = PRECISION(np.vstack([xgrid+fx, ygrid+fy]).T)
        H3x3_gg_flow, status = cv2.findHomography(pt0, pt1, cv2.RANSAC, 3.0)             
        H3x3_gg_flow = PRECISION(H3x3_gg_flow)  #from 64 bit float to 32 bit float
        print "H3x3_global_groundtruth:\n", H_gg_gt
        print "H3x3_global_flow:\n", H3x3_gg_flow
        
        #----------------------------------
        # Preparing loop...
        #----------------------------------
        NumBlksY, NumBlksX = (np.int32(ma.ceil(DimY/D)), np.int32(ma.ceil(DimX/D)))
        
        Cnt = 0
        for By in range(0,NumBlksY):
        #for By in range(7,7+2):
            for Bx in range(0,NumBlksX): 
                #print "Processing Block %d at %d,%d in frame %d/%d" % (Cnt,By,Bx,f,1) 
                print "%d " % Cnt

                PosB = np.eye(3, dtype=PRECISION)
                PosS = np.eye(3, dtype=PRECISION)
                Minus = np.eye(3, dtype=PRECISION)
                Minus[0,2] = -1.0;
                Minus[1,2] = -1.0;
                
                B_ref = Ref[By*D:By*D+D, Bx*D:Bx*D+D]
                B_cur = Cur[By*D:By*D+D, Bx*D:Bx*D+D]
                s = 2
                B_ref_search = Ref[By*D-s*D:By*D+s*D+D, Bx*D-s*D:Bx*D+s*D+D]
                B_cur_search = Cur[By*D-s*D:By*D+s*D+D, Bx*D-s*D:Bx*D+s*D+D] #required only for OptFlow
                            
                #----------------------------------
                # 1 | create H_bb from H_gg
                #----------------------------------
                #not used
                #PosB[0,2] = Bx*D;
                #PosB[1,2] = By*D;
                #H3x3_bb_gt = np.dot(Minus*PosB, np.dot(H3x3_gg_gt, PosB)) # i.e.: move block to correct position, warp, move back
                
    #             init_ECC_With_Groundtruth = False
    #             if init_ECC_With_Groundtruth:
    #                 H3x3_global = H3x3_g
    #             else:
    #                 H3x3_global = H3x3_flow
                
                #----------------------------------
                # 1 | create H_ss from H_gg (we need to have a H which is relativ to origin of search area!)
                #----------------------------------
                PosS[0,2] = Bx*D-s*D;
                PosS[1,2] = By*D-s*D;            
                H_ss_gt = np.dot(Minus*PosS, np.dot(H_gg_gt, PosS))
                
                #----------------------------------
                # 3 | create H_sb from H_ss (we need a H for warpPerspective() )
                #----------------------------------
                PosB[0,2] = s*D; #Attention: PosB must be relative to search area!
                PosB[1,2] = s*D; #Attention: PosB must be relative to search area!
                H_sb_gt = np.dot(Minus*PosB, np.dot(H_ss_gt, eye)) #this one is used for ECC init!

                            
                #----------------------------------
                # HACK: get the gb flow matrix (how does OptFlow perform?)
                #----------------------------------
                PosB[0,2] = Bx*D-s*D;
                PosB[1,2] = By*D-s*D;            
                H3x3_sb_flow = np.dot(Minus*PosB, np.dot(H3x3_gg_flow, PosB))
                PosB[0,2] = s*D; #relative to search area
                PosB[1,2] = s*D; #relative to search area
                H3x3_gb_flow = np.dot(Minus*PosB, np.dot(H3x3_sb_flow, eye))
    
                # We start ECC for normal blocks
                if np.array_equal(B_ref_search.shape, (s*D*2+D,s*D*2+D)):

                    # Write Blocks to disc
                    Ref_FN = "tmp/refblock.png" 
                    Cur_FN = "tmp/curblock.png" 
                    Ref_search_FN = "tmp/refsearch.png" 
                    Cur_search_FN = "tmp/cursearch.png" 
                    
                    #cv2.imwrite(Ref_FN, B_ref)
                    cv2.imwrite(Cur_FN, B_cur)
                    cv2.imwrite(Ref_search_FN, B_ref_search)
                    cv2.imwrite(Cur_search_FN, B_cur_search)
                    
                    #----------------------------------
                    # INVERSE 3+1 | Hsb to Hgg: Just testing, reconstructing H_gg_gt from ECC init H
                    #----------------------------------
                    # reconstructing is easy, just eliminate all terms left and right of H_gg by inverse matrices
                    PosB[0,2] = s*D; 
                    PosB[1,2] = s*D; 
                    Tmp1 = np.dot(invert(Minus*PosB)[1], np.dot(H_sb_gt, eye))
                    PosB[0,2] = Bx*D-s*D;
                    PosB[1,2] = By*D-s*D;  
                    Tmp2 = np.dot(invert(Minus*PosB)[1], np.dot(Tmp1, invert(PosB)[1]))
                
                    #----------------------------------
                    # Init and call ECC
                    #----------------------------------
                    #Init_FN = "tmp/F%02d_B%02d_init.txt" % (f, Cnt)
                    Init_FN = "tmp/ECC_init.txt"
                    (res, InvTmp) = invert(H_sb_gt)
                    print "Res=%d" % res
                    print "InvTmp=", InvTmp
                    cv2.cv.Save(Init_FN, cv.fromarray(InvTmp))
                    #cv2.cv.Save(Init_FN, cv.fromarray(invert(H3x3_gb_gt)[1]))
                    ret = os.system("C++/ecc -i " + Ref_search_FN + " -t " + Cur_FN +  
                              " -o tmp/warp.ecc -m affine -n 150 -v 0 -init " + Init_FN + " -oim tmp/warped.pgm") 
                    tmp = np.vstack((np.asarray(cv.Load("tmp/warp.ecc")), [0.0, 0.0, 1.0])) #make it a 3x3
                    H3x3_sb_ecc = invert(tmp)[1]
                    #assert(ret == 0)
                    
                    
                    #----------------------------------
                    #HACK
                    #----------------------------------
                    #H3x3_sb_ecc = H3x3_gb_gt
                    #print "Attention HACK!!"
                    
                    #----------------------------------
                    # 2 | Hbb to Hgg: Reconstructing H3x3_gg_ecc from ECC RESULT!
                    #----------------------------------
                    PosB[0,2] = s*D; 
                    PosB[1,2] = s*D; 
                    Tmp1 = np.dot(invert(Minus*PosB)[1], np.dot(H3x3_sb_ecc, eye))
                    PosB[0,2] = Bx*D-s*D;
                    PosB[1,2] = By*D-s*D;  
                    H3x3_gg_ecc = np.dot(invert(Minus*PosB)[1], np.dot(Tmp1, invert(PosB)[1]))
    #                 print "H3x3_gg_ecc:\n", H3x3_gg_ecc
    #                 print "H3x3_gg_gt:\n", H3x3_gg_gt
                    
                    #----------------------------------
                    # Get the noise of the transformed block corners
                    #----------------------------------
                    # 1 | Hgg to Hbb (search block to ref block) 
                    # ECC
                    PosB[0,2] = s*D; 
                    PosB[1,2] = s*D;             
                    H_bb_ecc = np.dot(Minus*PosB, np.dot(H3x3_sb_ecc, PosB))
                    # 1 | Hgg to Hbb (search block to ref block)     
                    # Groundtruth
                    PosB[0,2] = s*D; 
                    PosB[1,2] = s*D;             
                    H_bb_gt = np.dot(Minus*PosB, np.dot(H_sb_gt, PosB))  
                    
                    #TODO: get rid of relation to search area (only use Hbb's for warping) -> create functions!
                    # ORIGINAL: quad = PRECISION([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
                    #quad = PRECISION([[s*D+Bx*D, s*D+By*D], [s*D+Bx*D+D-1, s*D+By*D], [s*D+Bx*D+D-1, s*D+By*D+D-1], [s*D+Bx*D, s*D+By*D+D-1]])
                    quad = PRECISION([[0, 0], [D-1, 0], [0, D-1], [D-1, D-1]])
                    pts_gt  = cv2.perspectiveTransform(quad.reshape(1, -1, 2), H_bb_gt).reshape(-1, 2)
                    pts_ecc = cv2.perspectiveTransform(quad.reshape(1, -1, 2), H_bb_ecc).reshape(-1, 2)

                    #print "H3x3_gb_gt:\n", H3x3_gb_gt
                    #print "H3x3_bb_gt:\n", H3x3_bb_gt
                    #print "H3x3_bb_ecc:\n", H3x3_bb_ecc
                    #print "H3x3_bb_ecc*16:\n", H3x3_bb_ecc*16
                    #print "Diff:\n", (H3x3_bb_gt-H3x3_bb_ecc)
                    #print "DiffScaled:\n", (H3x3_bb_gt-H3x3_bb_ecc)*512
                                
                    #----------------------------------
                    # Lets warp and see how good we are
                    #----------------------------------                
                    B_ref_wrpd = cv2.warpPerspective(B_ref_search, H3x3_sb_ecc, (D, D), flags=self.WARP_INTERP)
                    #Block.B_ref_wrpd = B_ref_wrpd
                    (B_DimY, B_DimX) = B_ref.shape
                    Ref_wrpd_collection[By*D:By*D+B_DimY, Bx*D:Bx*D+B_DimX] = B_ref_wrpd[0:B_DimY, 0:B_DimX]
                
                Cnt += 1
                            
        #NOISE HACK
        #H3x3_gg_gt[0:2,0:3] = H3x3_gg_gt[0:2,0:3] * 1.0001  # add "noise"
        #H3x3_gg_gt[2:,0:2] = 0  # force affine
        #H3x3_gg_gt[0:2,0:3] = H3x3_gg_gt[0:2,0:3] * 1.0001  # add "noise"
        
        if self.showPlot:
        
            #----------------------------------
            # Create Matplotlib plot
            #----------------------------------        
            
            DiffImg1 = self.getDiffImage(Ref_wrpd_collection, Cur , eye)
            DiffImg2 = self.getDiffImage(Ref, Cur, H_gg_gt)
            
    
            
        #     fig = plt.figure(frameon=False)
        #     #fig.set_size_inches(1920,1080)
        #     ax = plt.Axes(fig, [0., 0., 1., 1.])
        #     ax.set_axis_off()
        #     fig.add_axes(ax)
            #plt.figure(figsize=(22,11.9))
            
            fig = plt.figure(figsize=(22,11.9))
            
            plt.subplot(2, 2, 1)
            plt.tight_layout()
            plt.axis('off')
            plt.imshow(DiffImg1)
            plt.set_cmap('jet')
            plt.colorbar()
            
            plt.subplot(2, 2, 3)
            plt.axis('off')
            plt.imshow(DiffImg2)
            #plt.set_cmap('pink')
            #plt.colorbar()
            
            plt.subplot(2, 2, 2)
            plt.axis('off')
            plt.imshow(draw_flow(Ref, Flow))
            
            plt.subplot(2, 2, 4)
            plt.axis('off')
            plt.imshow(draw_hsv(Flow))
        
            plt.show()
        #     mngr = plt.get_current_fig_manager()
        # # to put it into the upper left corner for example:
        #     mngr.window.setGeometry(0,0,1920, 950)
            
        #     ImgMatrix.fillPosition(DiffImg1, 0,0, "DiffImg Ref_wrpd_eccblocks - Cur")
        #     ImgMatrix.fillPosition(DiffImg2, 0,1, "DiffImg Ref_wrpd - Cur")
        #     ImgMatrix.fillPosition(draw_flow(Ref, Flow), 1,0, "draw_flow(gray, flow)")
        #     ImgMatrix.fillPosition(draw_hsv(Flow), 1,1, "VizFlow Colorwheel blocks")
        # 
        #     imshow('ImgMatrix', ImgMatrix.getFinal())
        #     imwrite("ImgMatrix.jpg",  ImgMatrix.getFinal())
        
            waitKey()
            destroyAllWindows()
    
#==========================================
if __name__ == '__main__':
#==========================================    

    import sys, os
    __builtins__.ProjectDir = os.path.abspath("../../")
    __builtins__.LibDir = ProjectDir + "/PythonLib"
    __builtins__.TmpDir = ProjectDir + "/tmp"
    sys.path.append(LibDir) 
    from Imports_Basic import *
    
    if 0:
        Generator = SequenceGenerator(ProjectDir + "/Various/Resources/BuzzOnTheMoon.jpg")
        Generator.OutputDir = ProjectDir + "/Various/YUVs_Tests2"
        pitch = yaw = roll = tx = ty = 0.0;
        H_accu_last = Generator.create_H_gt(pitch, yaw, roll, tx, ty) 
        roll = 5.0
        H_gt = Generator.create_H_gt(0, 0, roll, 0, 0)
        
        (Ref_F, H_F, Cur_F) = Generator.get_Ref_and_Cur(H_gt, H_accu_last)
        cv2.imwrite(TmpDir + "/Ref.png", Ref_F)
        cv2.imwrite(TmpDir + "/Cur.png", Cur_F)
        LumDiff = getWrpdLumDiff(Ref_F, Cur_F, H_F)
        cv2.imwrite(TmpDir + "/LumDiff.png", LumDiff)
        
        cv2.namedWindow('LumDiff', 0)
        cv2.imshow('LumDiff', LumDiff)
        cv2.waitKey()
    
    if 0:
        Generator = SequenceGenerator(ProjectDir + "/Various/Resources/HarrisonOnTheMoon1.jpg")
        Generator.OutputDir = ProjectDir + "/Various/YUVs"
        Generator.NumFrames = 6
        Generator.FinalSize=(1920 / 3, 1080 / 3)
        Generator.loadSourceImage() #reload, since we changed parameters
        Generator.verbose = True
        Generator.generateSequence()
        
    if 1:
        Generator = SequenceGenerator(ProjectDir + "/Various/Resources/Special/LMS_Logo.png")
        Generator.RescaleWidth=None
        Generator.OutputDir = ProjectDir + "/Various/YUVs"
        Generator.NumFrames = 6
        Generator.FinalSize=(640, 360)
        Generator.loadSourceImage() #reload, since we changed parameters
        Generator.generateSequence()