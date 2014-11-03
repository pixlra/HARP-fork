#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import os.path
from os.path import basename
import sys
import numpy as np
import shutil
import copy
import sys
import time

from General import *
from Plot import *
from Sequence import *

#taken from find_obj.py, no algorithmic changes
#==========================================
def applyRatioFilter(kp1, kp2, matches, ratio = 0.75):
#==========================================
    mkp1, mkp2 = [], []
    for m in matches:
        if (len(m) == 2 and m[0].distance < m[1].distance * ratio):  #if match looks good, keep it
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )  # remember keypoint in Cur img
            mkp2.append( kp2[m.trainIdx] )  # remember keypoint in Ref img
    p1 = np.float32([kp.pt for kp in mkp1])  # list of coordinates in Cur img (RANSAC needs this)
    p2 = np.float32([kp.pt for kp in mkp2])  # list of coordinates in Ref img (RANSAC needs this)
    kp_pairs = zip(mkp1, mkp2)  # interleave keypoints (creating pairs, Cur img kp, Ref img kp etc.)
    return p1, p2, kp_pairs 

#==========================================
def applyRatioFilterNEW(kp0, kp1, matches, ratio = 0.75):
#==========================================
    pass
    #mkp1, mkp2 = [], []
    NumFE = len(matches)
    p0 = np.zeros((NumFE, 2), np.float32)
    p1 = np.zeros((NumFE, 2), np.float32)
    status = np.zeros((NumFE), np.bool_)
    for idx, m in enumerate(matches):
        if len(m) != 2: #no match found
            continue
        
        p0[idx,:] = (kp0[m[0].queryIdx].pt[0], kp0[m[0].queryIdx].pt[1])
        p1[idx,:] = (kp1[m[0].trainIdx].pt[0], kp1[m[0].trainIdx].pt[1])
        #status[idx] = True if (m[0].distance < m[1].distance * ratio) else False
        isInlier = True if ((m[0].distance < m[1].distance * ratio)) else False
        #isInlier = True
        status[idx] = isInlier

    return p0, p1, status 

 
    
    
#==========================================
def getHomography(IDStr, Ref, Cur, Mask = None, H_GT = None):
#==========================================
    
    Y_ref = Ref[:,:,0]
    Y_cur = Cur[:,:,0]
    
    doVis = True
    before = time.clock()
    Ransac_Thresh = 10.0
    
    nOctaveLayers = 3
    nfeatures = 6000

    #============================
    # KLT
    #============================
    if IDStr == "KLT":
        back_threshold = 5.0
        
        before = time.clock()
         
        feature_params = dict( maxCorners = nfeatures,
                               qualityLevel = 0.01,
                               minDistance = 8,
                               blockSize = 19,
                               mask = Mask )
         
        lk_params = dict( winSize  = (19, 19),
                          maxLevel = 4,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        
        
        #-------------------------------------
        # DETECT & MATCH
        #-------------------------------------
        PREF_p0 = cv2.goodFeaturesToTrack(Y_ref, **feature_params)
        #if PREF_p0 is not None: 
        PREF_p1, st, err  = cv2.calcOpticalFlowPyrLK(Y_ref, Y_cur, PREF_p0, None, **lk_params)
    
        #-------------------------------------
        # PREFILTER
        #-------------------------------------   
        PREF_p0r, st, err = cv2.calcOpticalFlowPyrLK(Y_cur, Y_ref, PREF_p1, None, **lk_params)
        d = abs(PREF_p0-PREF_p0r).reshape(-1, 2).max(-1)
        PREF_status = d < back_threshold    
        
        PREF_p0 = PREF_p0.reshape(-1,2)
        PREF_p1 = PREF_p1.reshape(-1,2)
        print "%d of %d FE left after prefilter" % (np.sum(PREF_status), len(PREF_status))           
      
    #============================
    # SIFT, SURF, ORB
    #============================  
    else:
        FLANN_INDEX_KDTREE = 1
        FLANN_INDEX_LSH    = 6
        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        
        if IDStr == "SIFT":
            detector, matcher = cv2.SIFT(), cv2.BFMatcher(cv2.NORM_L2)
        elif IDStr == "ORB":
            detector, matcher = cv2.ORB(), cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        elif IDStr == "SURF":
            detector, matcher = cv2.SURF(), cv2.BFMatcher(cv2.NORM_L2)
    
        #-------------------------------------
        # DETECT & MATCH
        #-------------------------------------
        print "detecting keypoints..."
        #matcher = cv2.BFMatcher(cv2.NORM_L2) #cv2.ORB()
        kp0, desc0 = detector.detectAndCompute(Y_ref, Mask)
        kp1, desc1 = detector.detectAndCompute(Y_cur, Mask)
        print "NumFE: %d(cur), %d(ref), now matching..." % (len(kp0), len(kp1))
        raw_matches = matcher.knnMatch(desc0, trainDescriptors = desc1, k = 2)
        if len(kp0) == 0 or len(kp1) == 0:
            warning("No features found!!")
            #H, status = np.eye(3, dtype=float), None
    
        #-------------------------------------
        # PREFILTER
        #-------------------------------------
        #bypass = True if IDStr == "ORB" else False
  
        PREF_p0, PREF_p1, PREF_status = applyRatioFilterNEW(kp0, kp1, raw_matches) #PREF: prefilter
        print "%d of %d FE left after prefilter" % (np.sum(PREF_status), len(PREF_status))
           
        
    #============================
    # FIND HOMOGRAPHY
    #============================
    p0 = PREF_p0[PREF_status].copy()        
    p1 = PREF_p1[PREF_status].copy()  
    
    if len(p0) < 8:
        H, status = np.eye(3, dtype=float), None
        print "To few matches for RANSAC, H = eye"
    else:
        H, status = cv2.findHomography(p0, p1, cv2.RANSAC, Ransac_Thresh) 
        status = np.squeeze(status)
        print "%d of %d FE left after RANSAC" % (np.sum(status), len(status))

    consumed = time.clock() - before
    print "%s Duration: %0.3f" % (IDStr, consumed) 

    #============================
    # VISUALIZE
    #============================
    if doVis:
        vis_PREF_Matches = visualize_Matches(Y_ref, PREF_p0, PREF_p1, PREF_status) 
        vis_Matches      = visualize_Matches(Y_ref, p0, p1, status) 
        #UNUSED vis_MatchesZOOM = visualize_MatchesZOOM(Y_ref, p0, p1, status, 8, 0, 390)
        vis_Diff         = getWrpdLumDiff(Y_ref, Y_cur, H)
        
        CurBGR = cv2.cvtColor(Cur, cv2.COLOR_YUV2RGB)
        draw_WarpedOutline(CurBGR, H_GT, GREEN_BGR)
        draw_WarpedOutline(vis_Diff, H_GT, GREEN_BGR)
        draw_WarpedOutline(vis_Diff, H, RED_BGR, thickness=2)
        
        vs = getSpacer("Vertical", CurBGR)
        Vis  = np.hstack((vis_PREF_Matches, vs, vis_Matches, vs, vis_Diff))
        #Final  = np.hstack((CurBGR, vs, vis_PREF_Matches, vs, vis_Matches, vs, vis_Diff))
        #writeImg(Final, "getHomography_%s.png" % IDStr)
    else:
        Vis = 0
    
    return (H, Vis)    

#==========================================
def draw_WarpedOutline(Img, H, color=RED, thickness=8, corners=None):
#==========================================
    if H == None:
        return
    if corners == None:
        h, w = Img.shape[:2]
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) #manual 4x2 matrix
        cornersTest = np.zeros((4,2), np.float32) #for clarity: same result
        cornersTest[1,:] = [w, 0]
        cornersTest[2,:] = [w, h]
        cornersTest[3,:] = [0, h]
        assert(np.array_equal(corners,cornersTest) )
        #need integer values for cv2.polylines
        WRPD_corners     = np.int32( cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) )
        WRPD_cornersTest = np.int32( cv2.perspectiveTransform(cornersTest.reshape(1, -1, 2), H).reshape(-1, 2) )
        assert(np.array_equal(WRPD_corners,WRPD_cornersTest) )
        cv2.polylines(Img, [WRPD_corners], True, color, thickness=thickness)
    
#==========================================
def decompose_H(H, Phi_Thresh, Ratio_Thresh):
#==========================================
    (EigVals, EigVecs) = np.linalg.eig(H)
    
    AbsEigVals = abs(EigVals)
    idx = AbsEigVals.argsort()[::-1]
    #idx = EigVals.argsort()[::-1]
    EigVals = EigVals[idx]
    EigVecs = EigVecs[:,idx]
    
    col = 0 #largest eigenvalue
    EigVec = EigVecs[:,col] 
    EigVal = EigVals[col]
    factor = 1 / EigVec[2]
    Center = np.int32((EigVec*factor)[:2].real)

    Phi = np.angle(EigVals[1], deg=True) 
    Phi = np.sign(np.imag(EigVals[1])) * Phi
    Ratio = EigVals[0].real / EigVals[2].real
    
    print "H:\n" , H
    print "EigVecs:\n" , EigVecs
    print "EigVals:\n" , EigVals
    print "Center: %d,%d, Phi: %f" % (Center[0], Center[1], Phi) 
    print "Ration: %0.5f" % Ratio
    
    isZoom = 0
    isRotation = 0
    #if first EigVec way bigger and phi = 0: ZOOM
    if Ratio >= Ratio_Thresh and abs(Phi) < Phi_Thresh:
        print "ZOOMING"
        isZoom = 1
    #else if EigVec way bigger and abs(phi) > 1: ROTATION
    elif abs(Phi) >= Phi_Thresh:
        print "ROTATING"
        isRotation = 1
    #else: this is a translation or still frame
    else:
        print "NO SIGNIFICANT MOTION"

    return (isRotation, isZoom, Center, Phi, Ratio)

#==========================================
def write_H_gt(self, H_gt, BN, POC):
#==========================================
    FN = "groundtruth/%s/%s_POC%04d.H_gt" % (BN,BN, POC)
    np.save(FN, H_gt);
    
    #OpenCV YAML save
    #cv.Save("groundtruth/%s_POC%04d.H_gt" % (Name, POC), cv.fromarray(H_gt), name="H_gt", comment="")

#====================================================================================
# VISUALIZE        VISUALIZE        VISUALIZE
#====================================================================================

#taken from find_obj.py, no algorithmic changes
#==========================================
def visualize_Matches(Ref, p0, p1, status):
#==========================================
    Final = Ref.copy()
    Final = cv2.cvtColor(Final, cv2.COLOR_GRAY2RGB)
    
    thickness = 2
    arrowhead = 5
    
    p0_inlier  = p0[status]
    p1_inlier  = p1[status]
    p0_outlier = p0[np.logical_not(status)]
    p1_outlier = p1[np.logical_not(status)]
    
    #-------------------------------------
    # DRAW INLIER
    #-------------------------------------
    for (x0, y0), (x1, y1), inlier in zip(p0, p1, status):
        if inlier:
            col = GREEN_BGR
            drawArrow(Final, (x0, y0), (x1, y1), col, thickness, arrowhead)

#     test0 = zip(p0, p1, status)
#     test1 = zip(p0_inlier, p1_inlier)
# 
#     #-------------------------------------
#     # DRAW INLIER
#     #-------------------------------------
#     for (x0, y0), (x1, y1) in zip(p0_inlier, p1_inlier):
#             col = GREEN
#             drawArrow(Final, (x0, y0), (x1, y1), col, thickness, arrowhead)

    #-------------------------------------
    # DRAW OUTLIER
    #-------------------------------------
    for (x0, y0), (x1, y1), inlier in zip(p0, p1, status):
        if not inlier:
            col = RED_BGR
            drawArrow(Final, (x0, y0), (x1, y1), col, thickness, arrowhead)

    drawString(Final, (20, 20), "%d of %d FE left" % (np.sum(status), len(status)))
    return Final

#==========================================
def visualize_MatchesZOOM(Ref, p0, p1, status, Z, AnchorX, AnchorY):
#==========================================
    Final = Ref.copy()
    Resized = cv2.resize(Ref, (0, 0), fx=Z, fy=Z, interpolation=cv2.INTER_CUBIC)
    Resized = cv2.cvtColor(Resized, cv2.COLOR_GRAY2BGR)
    p0 = p0 * Z
    p1 = p1 * Z
    
    thickness = Z
    arrowhead = 10
    
    #-------------------------------------
    # DRAW INLIER
    #-------------------------------------
    for (x0, y0), (x1, y1), inlier in zip(p0, p1, status):
        if inlier:
            col = GREEN
            drawArrow(Resized, (x0, y0), (x1, y1), col, thickness, arrowhead, blueTip=True)

    (DimY, DimX) = Ref.shape[:2]
    Offx, Offy = AnchorX, AnchorY
    Final = Resized[Offy*Z:Offy*Z+DimY, Offx*Z:Offx*Z+DimX]
    return Final

#==========================================
def visualize_Rotation(Ref_YUV, Cur_YUV, H, Interp=cv2.INTER_LINEAR):
#==========================================
    eye = np.eye(3, dtype=np.float32)
    Ref = cv2.cvtColor(Ref_YUV, cv2.COLOR_YUV2RGB)
    Cur = cv2.cvtColor(Cur_YUV, cv2.COLOR_YUV2RGB)
    
    DimY, DimX = Ref.shape[:2]
    dx = DimX/4
    dy = DimY/1
    Cur_pad= cv2.copyMakeBorder(Cur, dy, dy, dx, dx, cv2.BORDER_CONSTANT, value=WHITE)
    Ref_pad= cv2.copyMakeBorder(Ref, dy, dy, dx, dx, cv2.BORDER_CONSTANT, value=BLACK)
    #plot_Img(Cur_pad,Block= True)
    #plot_Img(Ref_pad,Block= True)
    
                            
    #----------------------------------
    # 1 | Hgg to Hbb (picture to ref block)
    #----------------------------------
    BlockPos = np.eye(3, dtype=np.float32)
    Minus = np.eye(3, dtype=np.float32)
    Minus[0,2] = -1.0;
    Minus[1,2] = -1.0;
    BlockPos[0,2] = dx;
    BlockPos[1,2] = dy;
    H_bb = H
    H_gg = np.dot(np.linalg.inv(Minus*BlockPos), np.dot(H_bb, np.linalg.inv(BlockPos))) # i.e.: move block to correct position, warp, move back
    Warped_LumDiff = getWrpdLumDiff(Ref_pad, Cur_pad, H_gg, Interp=cv2.INTER_LINEAR)
    #plot_Img(Warped_LumDiff,Block= True)
    
    Ref_pad= cv2.copyMakeBorder(Ref, dy, dy, dx, dx, cv2.BORDER_CONSTANT, value=WHITE) #fix to make border white
    Warped_overlay = getWrpdOverlay(Ref_pad, Cur_pad, H_gg, Interp=cv2.INTER_LINEAR)
    #plot_ImgBGR(Warped_overlay,Block= True)
    
    #np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    corners = np.float32([[dx-1, dy-1], [dx-1+DimX, dy-1], [DimX+dx-1, DimY+dy-1], [dx-1, DimY+dy-1]])
    #corners = np.float32([[dy, dx], [dy,dx+DimX], [DimY+dy, DimX+dx], [DimY+dy, dx]])
    draw_WarpedOutline(Cur_pad, eye, BLUE_BGR, corners=corners)
    draw_WarpedOutline(Ref_pad, eye, GREEN_BGR, corners=corners)
    #draw_WarpedOutline(Ref_pad, H_gg, GREEN_BGR, corners=corners)
    draw_WarpedOutline(Warped_overlay, eye, BLUE_BGR, corners=corners)
    draw_WarpedOutline(Warped_overlay, H_gg, GREEN_BGR, corners=corners)
    draw_WarpedOutline(Warped_LumDiff, eye, BLUE_BGR, corners=corners)
    draw_WarpedOutline(Warped_LumDiff, H_gg, GREEN_BGR, corners=corners)
    
    eye = np.eye(3, dtype=np.float32)
    #vs = getSpacer("Vertical", CurBGR)
    FinalUpper  = np.hstack((Cur_pad, Ref_pad))
    FinalLower  = np.hstack((Warped_overlay, Warped_LumDiff))
    Final = np.vstack((FinalUpper, FinalLower))
    #plot_ImgBGR(Final,Block= True)

    return Final

#==========================================
def drawArrow(image, start, end, color, thickness=1, arrow_magnitude=2, line_type=8, shift=0, blueTip = False):
#==========================================    
    start = (int(start[0]), int(start[1])) #to int
    end = (int(end[0]), int(end[1])) #to int
    p, q = start, end
    cv2.line(image, p, q, color, thickness, line_type, shift) # draw arrow tail
    
    angle = np.arctan2(p[1]-q[1], p[0]-q[0]) # calc angle of the arrow 
    p = (int(q[0] + arrow_magnitude * np.cos(angle + np.pi/4)), # starting point of first line of arrow head
    int(q[1] + arrow_magnitude * np.sin(angle + np.pi/4)))
    color = BLUE if blueTip else color
    cv2.line(image, p, q, color, thickness, line_type, shift) # draw first half of arrow head
    p = (int(q[0] + arrow_magnitude * np.cos(angle - np.pi/4)), # starting point of second line of arrow head
    int(q[1] + arrow_magnitude * np.sin(angle - np.pi/4)))
    cv2.line(image, p, q, color, thickness, line_type, shift) # draw second half of arrow head

#==========================================
def test_getHomography():
#==========================================

    fn1 = '/home/dom/Desktop/Jetson_TK1/z_Res/Tohajiilee.jpg'
    fn2 = '/home/dom/Desktop/Jetson_TK1/z_Res/Tohajiilee_rotated.jpg'
    Ref = cv2.imread(fn1)
    Cur = cv2.imread(fn2)
    assert Ref != None
    assert Cur != None
    
    (H, Vis_Matches1) = getHomography("SIFT", Ref, Cur) 
#     (H, Vis_Matches2) = getHomography("ORB", Ref, Cur)
#     (H, Vis_Matches3) = getHomography("KLT", Ref, Cur)
    
    cv2.imwrite("./Vis_Matches1.png", Vis_Matches1)  
    cv2.namedWindow('Vis_Matches1', 0)
    cv2.imshow('Vis_Matches1', Vis_Matches1)
    cv2.waitKey()
   
#     writeImg(Vis_Matches, "KLT.png")
    #plot_Img(Vis_Matches, "test_getHomography")
    
    

#==========================================
if __name__ == '__main__':
#==========================================
    #sys.exit(0)
#     a = 'abcdef'
#     for x,y in zip(a[::2], a[1::2]):
#         print '%s%s' % (x,y)
    
    test_getHomography()
