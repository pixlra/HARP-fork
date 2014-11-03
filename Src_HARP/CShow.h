// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include <iostream>
#include <iomanip>
#include <typeinfo>
#include <vector>
#include <string>

#include "opencv/cv.hpp"
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/features2d/features2d.hpp"

//#include "TLibCommon/TypeDef.h"
#include "CShow_Conversion.h"

using namespace std;
using namespace cv;

extern const char *PartitionSizeStrings[];
extern const char *FalseTrueStrings[];

struct sCU
{
	// POC, CTU info
	UInt  POC;
	UInt  CTUIdx;      //CTU address (running index)
	Point CTUPos;       //absolute CTU position in pixels

	// CU position in frame, width, depth
	Point Pos;          //absolute CU position in pixels
	UInt  Width;        //CU dimension
	UInt  Depth;        //CU final depth

	// CU abs/raster partition indices, RelPos
	// everything is relative to upper left CTU corner
	UInt  AbsPartIdx;   //SU index, zorder scan
	UInt  RastPartIdx;  //SU index, raster scan
	Point RelPos;       //CU position relative to CTU

	// Mode
	string Mode;
};

struct sPU
{
  sCU CU;             //CU Info (PU belongs to this CU)

  Point Pos;          //absolute PU position in pixels
  Point Size;         //PU dimension

  // CU abs/raster partition indices, RelPos
  // everything is relative to upper left CTU corner
  UInt  AbsPartIdx;   //SU index, zorder scan
  UInt  RastPartIdx;  //SU index, raster scan
  Point RelPos;       //PU position relative to CTU
};

inline QString getString_GeneralInfo(TComDataCU* pcCU, UInt uiPartIdx);

inline void assertParameters(TComPic* rpcPic, Int iCUAddr)
{
  //LCU width and height, position of LCU in picture
  UInt uiWidthInLCUs  = rpcPic->getPicSym()->getFrameWidthInCU();
  UInt uiHeightInLCUs = rpcPic->getPicSym()->getFrameHeightInCU();

  //Asserting things (just making sure :)
  UInt uiTileCol;
  UInt uiTileStartLCU;
  UInt uiTileLCUX;
  UInt uiTileLCUY;
  UInt uiTileWidth;
  UInt uiTileHeight;
  uiTileCol = rpcPic->getPicSym()->getTileIdxMap(iCUAddr) % (rpcPic->getPicSym()->getNumColumnsMinus1()+1); // what column of tiles are we in?
  uiTileStartLCU = rpcPic->getPicSym()->getTComTile(rpcPic->getPicSym()->getTileIdxMap(iCUAddr))->getFirstCUAddr();
  uiTileLCUX = uiTileStartLCU % uiWidthInLCUs;
  uiTileLCUY = uiTileStartLCU / uiWidthInLCUs;
  assert( uiTileCol == 0 and uiTileStartLCU == 0 and uiTileLCUX == 0 and uiTileLCUY == 0);
  uiTileWidth = rpcPic->getPicSym()->getTComTile(rpcPic->getPicSym()->getTileIdxMap(iCUAddr))->getTileWidth();
  uiTileHeight = rpcPic->getPicSym()->getTComTile(rpcPic->getPicSym()->getTileIdxMap(iCUAddr))->getTileHeight();
}





#ifdef ACTIVATE_ABMC

inline void getWarpedCU(TComDataCU* pcCU, Mat H_gg, Mat Ref_Y, Mat Ref_U, Mat Ref_V, Mat &Y, Mat &U, Mat &V)
{
//  //TODO: extend to PU, currently: CU
//
//  // Get position of CU relative to frame origin (in pixels)
//  int LCU_x, LCU_y, AbsPart_x, AbsPart_y, CUWidth;
//  get_LCU_AbsPart_CUWidth(pcCU, LCU_x, LCU_y, AbsPart_x, AbsPart_y, CUWidth);
//  int pixel_x = LCU_x*64+AbsPart_x*4;
//  int pixel_y = LCU_y*64+AbsPart_y*4;
//
//  Mat M = Mat::eye(3, 3, CV_32F);
//  M.at<float>(0, 2) = -pixel_x;
//  M.at<float>(1, 2) = -pixel_y;
//
//  // Luminance Y
//  Mat H_gb = M * H_gg;
//  warpPerspective(Ref_Y, Y, H_gb, cv::Size(CUWidth,CUWidth), WARP_INTERP);
//
//  // Chrominance U+V
//  M.at<float>(0, 2) = -pixel_x/2;
//  M.at<float>(1, 2) = -pixel_y/2;
//
//  // we need to fix H due to subsampling
//  Mat H_fixed = H_gg.clone();
//  H_fixed.at<float>(0, 2) = H_fixed.at<float>(0, 2) / 2.0;
//  H_fixed.at<float>(1, 2) = H_fixed.at<float>(1, 2) / 2.0;
//
//  H_gb = M * H_fixed;
//
////  Mat C = Mat::eye(3, 3, CV_32F);
////  C.at<float>(0, 0) = 2;
////  C.at<float>(1, 1) = 2;
////  H_gb = M * H_gg ;
//  warpPerspective(Ref_U, U, H_gb, cv::Size(CUWidth/2,CUWidth/2), WARP_INTERP);
//  warpPerspective(Ref_V, V, H_gb, cv::Size(CUWidth/2,CUWidth/2), WARP_INTERP);
//
//  //note: Image has 16 bit bitdepth!
}

inline void get_WarpedPU()
{
//	//--------------------------------------------------
//	// OWN: REPLACE PRED BUFFER WITH WRPD-REC0
//	//--------------------------------------------------
////	assert(bSkipRes == false); // if this fires: back to the drawing board buddy
//
//	//
//	Mat Y, U, V;
//	getWarpedCU(pcCU, Global.H_gt, Global.Ref0_Y_Rec, Global.Ref0_U_Rec, Global.Ref0_V_Rec, Y, U, V);
//
//	copy_internal_yuv(MAT_2_HM, pcYuvPred, Y, Rect(), TEXT_LUMA);
//	copy_internal_yuv(MAT_2_HM, pcYuvPred, U, Rect(), TEXT_CHROMA_U);
//	copy_internal_yuv(MAT_2_HM, pcYuvPred, V, Rect(), TEXT_CHROMA_V);
}

#endif

// ==========================================================================
// IMPORTANT NOTE
// ==========================================================================
// Depth calculation inside RDO needs further analysis!
// Obviously, we are allowed to evaluate  depth=*(pcCU->getDepth())
// In a normal case (CShow_PUs and other), we would need to call  depth=pcCU->getDepth(AbsPartIdx);
// Up to now, we have not found a way to get the correct depth without AbsPartIdx in CShow_PUs
// It is unclear if this a code issue or a bug in HARP
//
// Workaround for now: creation of get_CU_Internal function with common code
// Results for RDO seem to fit
// Replicate issue with: run both functions, compare CU.depth values (sometimes different!)
//
// This issue needs instant attention!
// Clarify if CShow_RDO.h is broken!
// First clue: get_CU_RDO needs to be called with rpcTempCU, which may be special!

inline sCU get_CU_Internal(TComDataCU* pcCU, UInt Depth, UInt AbsPartIdx);

inline sCU get_CU_FIN(TComDataCU* pcCU, UInt AbsPartIdx)
{
	UInt Depth = pcCU->getDepth(AbsPartIdx);
	sCU CU = get_CU_Internal(pcCU, Depth, AbsPartIdx);

  if(pcCU->getPredictionMode(AbsPartIdx) == MODE_INTRA)
    CU.Mode = "Intra";
  else if(pcCU->getPredictionMode(AbsPartIdx) == MODE_INTER && pcCU->isSkipped(AbsPartIdx))
    CU.Mode = "Skip";
  else if(pcCU->getPredictionMode(AbsPartIdx) == MODE_INTER && pcCU->getMergeFlag(AbsPartIdx))
    CU.Mode = "Merge";
  else if(pcCU->getPredictionMode(AbsPartIdx) == MODE_INTER)
    CU.Mode = "Inter";
  else
    assert(0);

	return CU;
}

inline sCU get_CU_RDO(TComDataCU* pcCU)
{
	UInt Depth = *pcCU->getDepth();
	UInt AbsPartIdx = pcCU->getZorderIdxInCU();
	sCU CU = get_CU_Internal(pcCU, Depth, AbsPartIdx);
	return CU;
}

inline Point getRelPos(UInt RastPartIdx)
{
	Point RelPos_inSU, RelPos;
	RelPos_inSU.x = RastPartIdx % (CTU_DIM/SU_DIM); // 64/4 == number of storage units in CTU
	RelPos_inSU.y = RastPartIdx / (CTU_DIM/SU_DIM);

	RelPos.x = RelPos_inSU.x * SU_DIM;
	RelPos.y = RelPos_inSU.y * SU_DIM;

	return RelPos;
}

inline sCU get_CU_Internal(TComDataCU* pcCU, UInt Depth, UInt AbsPartIdx)
{
	sCU CU;

	CU.Depth = Depth;
	CU.AbsPartIdx = AbsPartIdx;
	CU.Width = 64 >> CU.Depth; //width of CU in pixels

	//Alternative way, not tested:
	//UInt PosX = pcCU->getCUPelX() + g_auiRasterToPelX[ g_auiZscanToRaster[uiAbsPartIdx] ];
    //UInt PosY = pcCU->getCUPelY() + g_auiRasterToPelY[ g_auiZscanToRaster[uiAbsPartIdx] ];

	//Getting the pcPic, POC and iCUAddr
	TComPic* rpcPic = pcCU->getPic();
	CU.POC = rpcPic->getPOC();
	CU.CTUIdx = pcCU->getAddr(); //warning: bad naming, address of LCU ONLY!
	assertParameters(rpcPic, CU.CTUIdx);

	//width and height in CTUs
	UInt Width_inCTUs  = rpcPic->getPicSym()->getFrameWidthInCU();
	UInt Height_inCTUs = rpcPic->getPicSym()->getFrameHeightInCU();

	//Getting Raster Part Index
	CU.RastPartIdx  = g_auiZscanToRaster[CU.AbsPartIdx];

	//Find out the position of the CTU
	CU.CTUPos.x = (CU.CTUIdx % Width_inCTUs) * CTU_DIM;
	CU.CTUPos.y = (CU.CTUIdx / Width_inCTUs) * CTU_DIM;

	CU.RelPos = getRelPos(CU.RastPartIdx);

	CU.Pos.x = CU.CTUPos.x + CU.RelPos.x;
	CU.Pos.y = CU.CTUPos.y + CU.RelPos.y;

	//DEBUG:
	//printf("Basic CU Info: CU.Pos.x=%d CU.Pos.y=%d CU.Width=%d CU.Depth=%d \n", CU.Pos.x, CU.Pos.y, CU.Width, CU.Depth );

	return CU;
}

inline UInt calculateHADs_Y( TComYuv* pcRef, TComYuv* pcCur, UInt uiPartAddr, Int Rows, Int Cols)
//(Pel* piOrg, Pel* piCur, Int  iRows, Int  iCols, iStrideCur, iStrideOrg )
{
  //adapted from: UInt TComRdCost::xGetHADs( DistParam* pcDtParam )

  DistParam DtParam;
  DistParam *pcDtParam = &DtParam ;
  pcDtParam->bApplyWeight = false;
  pcDtParam->pOrg = pcRef->getLumaAddr(uiPartAddr);
  pcDtParam->pCur = pcCur->getLumaAddr(uiPartAddr);
  pcDtParam->iRows = Rows;
  pcDtParam->iCols = Cols;
  pcDtParam->iStrideOrg =  pcRef->getStride();
  pcDtParam->iStrideCur =  pcCur->getStride();
  pcDtParam->iStep = 1; //LUMA
  pcDtParam->bitDepth = 8;

  UInt HAD_SAD = TComRdCost::xGetHADs(pcDtParam);
  return HAD_SAD;
}

  inline string getString_PartitionSize(TComDataCU* pcCU, UInt uiAbsZorderIdx)
  {
    //NOTE: uiPartIdx is the same as uiAbsZorderIdx!
    char text[500];
    sprintf(text, "PU Partitions: %s\n", PartitionSizeStrings[pcCU->getPartitionSize(uiAbsZorderIdx)]);
    return string(text);
  }

  inline QString getString_GeneralInfo(TComDataCU* pcCU, UInt uiPartIdx)
  {
    //NOTE: uiPartIdx is the same as uiAbsZorderIdx!
    UInt  uiPartAddr;
    Int   iRoiWidth, iRoiHeight;
    pcCU->getPartIndexAndSize( uiPartIdx, uiPartAddr, iRoiWidth, iRoiHeight );

    PartSize ePartSize = pcCU->getPartitionSize(0);
    UInt NumPU = ( ePartSize == SIZE_2Nx2N ? 1 : ( ePartSize == SIZE_NxN ? 4 : 2 ) );

    QString Info;
    Info += QString("CTU-Addr=%1 \n")
                            .arg(pcCU->getAddr());
    Info += QString("CU-Depth=%2 | CU-Dims=%3x%4 \n")
                            .arg(pcCU->getDepth(uiPartIdx))
                            .arg(pcCU->getWidth(uiPartIdx))
                            .arg(pcCU->getHeight(uiPartIdx));
    Info += QString("%1 (part size) | PU %2 of %3 \n")
                      .arg(PartitionSizeStrings[pcCU->getPartitionSize(0)])
                      .arg(uiPartIdx+1)
                      .arg(NumPU);
    return Info;
  }

  inline void myGetPartIndexAndSize( TComDataCU* pcCU, UInt uiAbsZorderIdx, UInt uiDepth,
                              UInt PUIdx, //PUIdx: PU index, maybe just one, maybe up to four
                              UInt& ruiPartAddr, Int& riWidth, Int& riHeight )
  {
    PartSize ePartSize = pcCU->getPartitionSize( uiAbsZorderIdx );

    unsigned char Width  = pcCU->getWidth(uiAbsZorderIdx);
    unsigned char Height = pcCU->getHeight(uiAbsZorderIdx);

    TComPic* pcPic     = pcCU->getPic();
    UInt NumPartInCTU  = pcPic->getNumPartInCU();      //number of StorageUnits (4x4) in CTU
    UInt NumPartInCU = NumPartInCTU >> (uiDepth<<1); //number of StorageUnits (4x4) in current CU

    switch ( ePartSize )
    {
      case SIZE_2NxN:
        riWidth = Width;
        riHeight = Height >> 1;
        ruiPartAddr = ( PUIdx == 0 )? 0 : NumPartInCU >> 1;
        break;
      case SIZE_Nx2N:
        riWidth = Width >> 1;
        riHeight = Height;
        ruiPartAddr = ( PUIdx == 0 )? 0 : NumPartInCU >> 2;
        break;
      case SIZE_NxN:
        riWidth = Width >> 1;
        riHeight = Height >> 1;
        ruiPartAddr = ( NumPartInCU >> 2 ) * PUIdx;
        break;
      case SIZE_2NxnU:
        riWidth     = Width;
        riHeight    = ( PUIdx == 0 ) ?  Height >> 2 : ( Height >> 2 ) + ( Height >> 1 );
        ruiPartAddr = ( PUIdx == 0 ) ? 0 : NumPartInCU >> 3;
        break;
      case SIZE_2NxnD:
        riWidth     = Width;
        riHeight    = ( PUIdx == 0 ) ?  ( Height >> 2 ) + ( Height >> 1 ) : Height >> 2;
        ruiPartAddr = ( PUIdx == 0 ) ? 0 : (NumPartInCU >> 1) + (NumPartInCU >> 3);
        break;
      case SIZE_nLx2N:
        riWidth     = ( PUIdx == 0 ) ? Width >> 2 : ( Width >> 2 ) + ( Width >> 1 );
        riHeight    = Height;
        ruiPartAddr = ( PUIdx == 0 ) ? 0 : NumPartInCU >> 4;
        break;
      case SIZE_nRx2N:
        riWidth     = ( PUIdx == 0 ) ? ( Width >> 2 ) + ( Width >> 1 ) : Width >> 2;
        riHeight    = Height;
        ruiPartAddr = ( PUIdx == 0 ) ? 0 : (NumPartInCU >> 2) + (NumPartInCU >> 4);
        break;
      default:
        assert ( ePartSize == SIZE_2Nx2N );
        riWidth = Width;
        riHeight = Height;
        ruiPartAddr = 0;
        break;
    }
  }

//------------------------------------------------------------------------------
//  VISUALIZATION CODE
//------------------------------------------------------------------------------

inline void getVis_CurrentCU(TComDataCU* pcCU, Mat &Vis_Image)
{
  sCU CU = get_CU_RDO(pcCU);

  //Getting original pixel values of LCU
  Mat PicYuvOrg;
  copy_PicYuv2Mat(pcCU->getPic()->getPicYuvOrg(), PicYuvOrg, INTER_NEAREST);
  convertToCV_8UC3(PicYuvOrg);
  Mat PicYuvOrgROI = PicYuvOrg(Rect(CU.CTUPos.x, CU.CTUPos.y, CTU_DIM, CTU_DIM));

  cvtColor(PicYuvOrgROI, Vis_Image, CV_YCrCb2RGB);
  Mat TinyROI = Vis_Image(Rect(CU.RelPos.x, CU.RelPos.y, CU.Width, CU.Width));

  //Let's decide on a color, color-fanboy!
  Scalar color(128,128,128); //grey
  if(pcCU->getPredictionMode(0) == MODE_INTRA)
    color = Scalar(0,0,255); // red
  else if(pcCU->getPredictionMode(0) == MODE_INTER && pcCU->isSkipped(0))
    color = Scalar(0,255,0); // green
  else if(pcCU->getPredictionMode(0) == MODE_INTER)
    color = Scalar(255,0,0); // blue

  //Coloring CU Border
  Mat Tmp = TinyROI.clone();
  TinyROI = color; //full color splil yo
  Tmp(Rect(2, 2, TinyROI.cols - 4, TinyROI.rows - 4)).copyTo(TinyROI(Rect(2, 2, TinyROI.cols - 4, TinyROI.rows - 4)));
}

inline void getVis_CurrentPU(TComDataCU* pcCU, Int iPartIdx, QString Headline, Mat &Vis_Image, Mat &Vis_Text)
{
  getVis_CurrentCU(pcCU, Vis_Image);

  //it's a bird, it's a plane, its... a PREDICTION UNIT MAN!
  //off we go, looking at our PU in detail
  UInt  uiPartAddr;
  Int   iRoiWidth, iRoiHeight;
  pcCU->getPartIndexAndSize( iPartIdx, uiPartAddr, iRoiWidth, iRoiHeight );
  UInt uiAbsZorderIdx = pcCU->getZorderIdxInCU();
  int RasterPartIdx  = g_auiZscanToRaster[uiAbsZorderIdx+uiPartAddr];

  //drawing current PU
  int SUnitsPerRow = 64/4; // 64/4 = 16 StorageUnits in a CTB row
  Point PU_Anc  = Point(RasterPartIdx % (SUnitsPerRow), RasterPartIdx / (SUnitsPerRow)) * 4;
  Point PU_Dims = Point(iRoiWidth , iRoiHeight );

  //Yeah! We just found out how to calculate PU positions without recursion!
  PartSize ePartSize = pcCU->getPartitionSize( 0 );
  UInt NumPU = ( ePartSize == SIZE_2Nx2N ? 1 : ( ePartSize == SIZE_NxN ? 4 : 2 ) );
  UInt NextPU_Increment = ( g_auiPUOffset[UInt( ePartSize )] << ( ( pcCU->getSlice()->getSPS()->getMaxCUDepth() - pcCU->getDepth(iPartIdx) ) << 1 ) ) >> 4;

  //Coloring PU Border
  Mat PU_Roi = Vis_Image(Rect(PU_Anc.x, PU_Anc.y, PU_Dims.x, PU_Dims.y));
  Mat Tmp2 = PU_Roi.clone();
  PU_Roi = RED; //full color spill yo
  Tmp2(Rect(1, 1, PU_Roi.cols - 2, PU_Roi.rows - 2)).copyTo(PU_Roi(Rect(1, 1, PU_Roi.cols - 2, PU_Roi.rows - 2)));

  // create Vis_Text
  Vis_Text = Mat(VIS_TEXT_SIZE, CV_8UC3, Scalar(128,128,128));
  QString Info = QString(Headline) + "\n";
  Info += QString("Blue: cur-CU | Red: cur-PU\n");
  Info += getString_GeneralInfo(pcCU, iPartIdx);
  Info += QString("uiAbsZorderIdx=%1 \n").arg(uiAbsZorderIdx);
  Info += QString("uiPartAddr=%1 | RasterPartIdx=%2\n").arg(uiPartAddr).arg(RasterPartIdx);
  for ( UInt uiPartIdx = 0, uiSubPartIdx = uiAbsZorderIdx; uiPartIdx < NumPU; uiPartIdx++, uiSubPartIdx += NextPU_Increment )
    Info += QString("Processing PU %1 \n").arg(uiPartIdx);

  writeText(Vis_Text, Info, 2.0);
}

inline void getVis_YUVBuffer(TComDataCU* pcCU, TComYuv* pcYuv, QString Headline, Mat &Vis_Image, Mat &Vis_Text)
{
  //create Vis_Image
  copy_Yuv2Mat(pcYuv, Vis_Image, INTER_NEAREST);

  convertToCV_8UC3(Vis_Image);
  cvtColor(Vis_Image, Vis_Image, CV_YCrCb2RGB);

  // create Vis_Text
  int iHeight = pcYuv->m_iHeight;
  int iWidth  = pcYuv->m_iWidth;
  int iStride = pcYuv->m_iWidth;

  assert( iHeight == iStride && iWidth == iStride);

  Vis_Text = Mat(VIS_TEXT_SIZE, CV_8UC3, Scalar(128,128,128));
  QString Info = QString(Headline) + "\n";
  Info += QString("Dims: %1x%2\n").arg(iHeight).arg(iWidth);
  Info += QString("Stride: %1\n").arg(iStride);
  writeText(Vis_Text, Info, 2.0);
}

inline void getVis_SingleYUVBuffers(TComDataCU* pcCU, TComYuv* pcYuv, Mat &Y, Mat &U, Mat &V, bool doRescaleAndShift)
{
  copy_internal_yuv(HM_2_MAT, pcYuv, Y, Rect(), TEXT_LUMA);
  copy_internal_yuv(HM_2_MAT, pcYuv, U, Rect(), TEXT_CHROMA_U);
  copy_internal_yuv(HM_2_MAT, pcYuv, V, Rect(), TEXT_CHROMA_V);

  //note that we already have a difference buffer here!
  if(doRescaleAndShift)
  {
    Y = (Y / 2) + 128;
    U = (U / 2) + 128;
    V = (V / 2) + 128;
  }

  //HACK
//  Y.convertTo(Y, CV_8U);
//  U.convertTo(U, CV_8U);
//  V.convertTo(V, CV_8U);
//
//  equalizeHist( Y, Y );
//  equalizeHist( U, U );
//  equalizeHist( V, V );
}


inline Mat getLumDifference(Mat Img1, Mat Img2)
{
  vector<Mat> splitted;

  split(Img1, splitted);
  Mat Y1 = splitted[0].clone() / 2;
  split(Img2, splitted);
  Mat Y2 = splitted[0].clone() / 2;

  int Contrast = 1;
  Mat YDiff = ((Y1 - Y2)*Contrast)+128;

  Mat VisDiff;
  Mat pointers[] = { YDiff, YDiff, YDiff };
  merge(pointers, 3, VisDiff);

  return VisDiff;
}

inline void getVis_subtractYBuffers(TComDataCU* pcCU, TComYuv* pcYuv1, TComYuv* pcYuv2, QString Headline, Mat &Vis_Image, Mat &Vis_Text)
{
  Mat Yuv1, Yuv2;
  copy_Yuv2Mat(pcYuv1, Yuv1, INTER_NEAREST);
  copy_Yuv2Mat(pcYuv2, Yuv2, INTER_NEAREST);

  vector<Mat> splitted;

  split(Yuv1, splitted);
  Mat Y1 = splitted[0].clone() / 2;
  split(Yuv2, splitted);
  Mat Y2 = splitted[0].clone() / 2;

  int Contrast = 1;
  Mat YDiff = ((Y1 - Y2)*Contrast)+128;

  Mat pointers[] = { YDiff, YDiff, YDiff };
  merge(pointers, 3, Vis_Image);

  convertToCV_8UC3(Vis_Image);

  Vis_Text = Mat(VIS_TEXT_SIZE, CV_8UC3, Scalar(128,128,128));
  QString Info = QString(Headline) + "\n";
  writeText(Vis_Text, Info, 2.0);
}




