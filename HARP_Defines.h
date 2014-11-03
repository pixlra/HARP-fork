// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

// FOR FURTHER CONTROL, SEE COMMAND LINE ARGUMENTS, E.G.:
// --HARP_ObsPOCs=0,1,2 --HARP_ObsCTUs=5
// --HARP_PUs --HARP_TUs --HARP_RefIndices --HARP_UnitCloseup
// --HARP_RDO
// --HARP_CleanTmpDir

// CTD : Comment to deactivate
// VAD : Value-controlled define

// for rate curves, add --HARP_RateCurves to cmd line
// this will disable all images and the cleanup of the tmp dir

#define ME_TRANSL 0
#define ME_AFFINE 1
#define ME_NUM    2

// PRIMARY CONTROL =========================================
#define HARP_VERSION "1.01"     //VAD, HARP version
#define ACTIVATE_HARP        //CTD, deactivate to get normal HM speed
//#define ACTIVATE_HARPGUI   //CTD, show minimal C++ HARP GUI

// ==========================================================

// PYTHON CONTROL ===========================================
#define CBCR_INTERPOLATION  INTER_NEAREST //VAD, will not harm original values
#define EXPORT_RDO_PKL 1 //VAD, specify if you want additional PyCUs with RDO info
// ==========================================================

// CALLGRIND CONTROL ========================================
//#define ACTIVATE_CALLGRIND       //CTD, activate callgrind profiling (linux-only)
//#define CG_CALLGRAPH_INTER_ONLY  //CTD, skip Intra POCs during Callgrind profiling
// ==========================================================


// VISUALIZATION CONTROL ===================================
#define VIS_TEXT_SIZE 600,600   //VAD, size of text info image patch
#define KEEP_IMAGES           //CTD, additionally output POC-enumerated images
// ==========================================================

// JPG/PNG CONTROL =========================================
#define IMAGE_FORMAT ".jpg" //VAD, choose between .jpg and .png
#define JPG_QUALITY 95      //VAD, name says it all
//REMOVE ME #define SKIP_JPEGS 0        //VAD, manual kill switch for JPGs (rate curves on cluster)
//REMOVE ME #define JPG_DIMX 1920     //CTD, force JPGs to certain width (for HD, UHD)
#define IS_INVERTING false  //VAD, Jo, Mr White!
// ==========================================================

// NEXT DEVELOPMENT BRANCH ==================================
#ifdef ACTIVATE_NEXT //CMakeLists has full control here
  #define DISABLE_MERGE
	#define ACTIVATE_ABMC
	#define WARP_INTERP CV_INTER_CUBIC // choose: INTER_AREA //INTER_LANCZOS4 //INTER_LINEAR //INTER_CUBIC
#endif
// ==========================================================

// RESTRICTIONS =============================================
// WARNING: do NOT change, this will break the code
#define CTU_DIM 64 //VAD, CTU size
#define SU_DIM 4   //VAD, interal storage unit size
// ==========================================================

// DEPRECATED ===============================================
//#define DO_xMotionEstimation
//#define COUT(instruction) //cout instruction
//#define COUT_MATRIX(instruction) //cout instruction   //print all sorts of H matrices
//#define PROCESS_PRIORITY 20 //lower=higher prio
// ==========================================================

// TIMER STUFF

#define INIT_TIMER struct timeval tp; \
        double sec, usec, start, end, Seconds;
#define START_TIMER \
		    /*cout << "TIMER: starting...\n";*/ \
		    gettimeofday( &tp, NULL ); \
        sec = static_cast<double>( tp.tv_sec ); \
        usec = static_cast<double>( tp.tv_usec )/1E6; \
        start = sec + usec;
#define STOP_TIMER(text) \
		gettimeofday( &tp, NULL ); \
        sec = static_cast<double>( tp.tv_sec ); \
        usec = static_cast<double>( tp.tv_usec )/1E6; \
        end = sec + usec; \
        Seconds = end - start; \
        cout << "TIMER stopped: " << text << " took  "; \
        cout << Seconds << " secs" << endl << flush;

// VARIOUS
//#define FOR(i,length) for(int i=0; i<(int)(length); i++)
#define CTUSIZE 64 // KNOW WHAT YOU ARE DOING!
#define THROW_ERROR(error) {std::cout << endl << "ERROR: " << endl << error << endl << "Exiting..." << endl << endl << endl << flush; assert(0); exit(-1);}
#define THROW_ERROR_PYTHON(error, moreinfo) {PyErr_Print(); std::cout << endl << "PYTHON ERROR: " << endl << error << " (" << moreinfo << ")" << endl << "Exiting..." << endl << endl << endl << flush; assert(0); exit(-1);}
//
// 5BB920X

// BASIC COLOR CODES
#define WHITE Scalar(255,255,255)
#define GRAY  Scalar(128,128,128)
#define BLACK Scalar(0,0,0)
#define YELLOW Scalar(0,255,255)
#define GREEN Scalar(0,255,0)
#define DARKGREEN Scalar(0,128,0)
#define RED Scalar(0,0,255)
#define BLUE Scalar(255,0,0)
#define GREEN_2 Scalar(9,241,9)
#define DEEPSKYBLUE Scalar(255,191,0)
#define DARKORANGE Scalar(0,140,255)
#define OLIVE Scalar(0x00,0x80,0x80)
#define MEDIUMPURPLE Scalar(0xD8,0x70,0x93)
#define MAGENTA Scalar(255,0,255)
#define BRBA_YELLOW Scalar(13,201,250)
#define BRBA_BLUE Scalar(194,189,44)
#define BRBA_RED Scalar(52,97,220)
#define BRBA_GREEN Scalar(63,168,125)

/*
--HARP_TmpDir=tmp
--HARP_PUs
--HARP_RefIndices
--HARP_UnitCloseup
--HARP_ObsPOCs=1
--HARP_ObsCTUs=14
--HARP_RDO
--HARP_CleanTmpDir
-i ../LMS/z_Various/LMS_640x360.yuv -wdt 640 -hgt 360 -f 6 -c ../HM/cfg/encoder_lowdelay_P_main.cfg  --QP=10 -b tmp/str.bin  -fr 30 --InputBitDepth=8
*/


#include "CGlobal.h" //pull in all global stuff wherever HARP_Defines.h is interesting


