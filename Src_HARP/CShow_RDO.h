// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include <iostream>
#include <iomanip>
#include <typeinfo>
#include <vector>

#include "HARP_Defines.h"
#include "CHelper.h"
#include "TLibCommon/TypeDef.h"
#include "CShow.h"

using namespace std;
using namespace cv;

class CShow_RDO
{
public:
  int LCU_DimX;
  int LCU_DimY;
  int call;
  CImgMatrix ImgMatrix;
  int CurrentImgRow;
  char text[500];

  CShow_RDO()
  {
    string ClassName = "CShow_RDO";
    //cout << "\n-------- " << ClassName << " instantiated "  << " -----------\n";

    LCU_DimX = LCU_DimY = 64;
    ImgMatrix.Cols = 11;

    //cout << "----------------------------------------------------------\n\n";
    call++;
  }

  void initAnalysis(TComDataCU* pcCU)
  {
    if (not Global.isObsCTU())
      return;
  }

  void finalizeAnalysis(TComDataCU* pcCU)
  {
    if (not Global.isObsCTU())
      return;

    //---------------------------------------------
    // EXPORTING IMAGES
    //---------------------------------------------
    // since ImgMatrix takes over splitting, we do this manually!
	char POCStr[500], CTUStr[500];
	sprintf(POCStr, "POC%05d_", Global.getCurrentPOC());
	sprintf(CTUStr, "_CTU%04d", Global.getCurrentCTU());
	ImgMatrix.saveFinal(Global.TmpDir + POCStr + "CheckRDCostInter" + CTUStr + IMAGE_FORMAT);


    ImgMatrix.reset();
  }

  void createImg_predInterSearch( TComDataCU* pcCU, TComYuv* pcOrgYuv, TComYuv*& rpcPredYuv,
                                  TComYuv*& rpcResiYuv, TComYuv*& rpcRecoYuv, Bool bUseRes, Bool bUseMRG,
                                  Int iPartIdx)
  {
    if (not Global.isObsCTU())
      return;
    Mat Vis1, Vis2, VisText;

    //Create Headline
    Int         iWidth, iHeight;
    UInt        uiPartAddr;
    pcCU->getPartIndexAndSize( iPartIdx, uiPartAddr, iWidth, iHeight );
    PartSize ePartSize = pcCU->getPartitionSize(0);
    QString PartSizeString = PartitionSizeStrings[ePartSize];
//    if(Global.isCurrentTestAffine)
//      PartSizeString += "_AFFINE";
    QString Headline = QString("predInterSearch(): POC%1, CTU%2, %3, Depth%4, Merge=%5")
        .arg(Global.CurrentPOC).arg(Global.CurrentCTU)
        .arg(PartSizeString).arg(pcCU->getDepth(0)).arg(pcCU->getMergeFlag( 0 ));
    this->ImgMatrix.createEmptyRow(Headline, BRBA_YELLOW);

    getVis_CurrentPU(pcCU, iPartIdx, "getVis_CurrentPU", Vis1, VisText);
    ImgMatrix.pushImg(Vis1, "Current PU");
    Mat KeepImg = VisText.clone();

    getVis_YUVBuffer(pcCU, pcOrgYuv, "getVis_YUVBuffer ORG", Vis1, VisText);
    ImgMatrix.pushImg(Vis1, "ORG");

    //TODO: Visualize CU in Ref0 Frame
    //Pel*        piRefY      = pcCU->getSlice()->getRefPic( eRefPicList, iRefIdxPred )->getPicYuvRec()->getLumaAddr( pcCU->getAddr(), pcCU->getZorderIdxInCU() + uiPartAddr );
    //Int         iRefStride  = pcCU->getSlice()->getRefPic( eRefPicList, iRefIdxPred )->getPicYuvRec()->getStride();

    getVis_YUVBuffer(pcCU, rpcPredYuv, "getVis_YUVBuffer PRED", Vis1, VisText);
    ImgMatrix.pushImg(Vis1, "PRED");

    getVis_subtractYBuffers(pcCU, pcOrgYuv, rpcPredYuv, "getVis_YUVBuffer DIFFERENCE", Vis1, VisText);
    ImgMatrix.pushImg(Vis1, "ORG-PRED Y");

//    getVis_YUVBufferWarped(pcCU, pcOrgYuv, "getVis_YUVBuffer WARPED", Vis1, Vis2);
//    ImgMatrix.pushImg(Vis1, "REF0WRPD");
//    ImgMatrix.pushImg(Vis2, "ORG-REF0WRPD Y");

    ImgMatrix.pushImg(KeepImg, "");

    // MV Info
    TComMv cMv  = pcCU->getCUMvField( REF_PIC_LIST_0 )->getMv( uiPartAddr );
    Point Mv(cMv.getHor(), cMv.getVer());

    // create InfoImg
//    Mat InfoImg(VIS_TEXT_SIZE, CV_8UC3, Scalar(128,128,128));
//    QString Info = QString("Best PU-MV in LIST0: %1,%2 \n").arg(Mv.x).arg(Mv.y);
//    writeText(InfoImg, Info, 2.0);
//    ImgMatrix.pushImg(InfoImg, "Further info");

  }
                          // pcCU             pcYuvOrg,          pcYuvPred,          rpcYuvResi,
  void createImg_encodeRes( TComDataCU* pcCU, TComYuv* pcOrgYuv, TComYuv* pcPredYuv, TComYuv*& rpcResiYuv,
		  // rpcYuvResiBest,        rpcYuvRec,				  //encodeRes may decide against coefficient coding
		  TComYuv*& rpcResiBestYuv, TComYuv*& rpcRecYuv, bool skipCoeffCoding)
  {
    Mat Vis_Image, Vis_Text;
    Mat Y, U, V;

    //HACK to only show non-merge related runs
//    if(pcCU->getMergeFlag( 0 ) == true)
//      return;

    //Create Headline
    PartSize ePartSize = pcCU->getPartitionSize(0);
    QString PartSizeString = PartitionSizeStrings[ePartSize];
//    if(Global.isCurrentTestAffine)
//      PartSizeString += "_AFFINE";
    QString Headline = QString("encodeRes(): POC%1, CTU%2, %3, Depth%4, Merge=%5, skipCoeffCoding=%6")
        .arg(Global.CurrentPOC).arg(Global.CurrentCTU)
        .arg(PartSizeString).arg(pcCU->getDepth(0)).arg(pcCU->getMergeFlag( 0 )).arg(skipCoeffCoding);
    this->ImgMatrix.createEmptyRow(Headline, BRBA_GREEN);

    //VISUALIZE CURRENT CU
    getVis_CurrentCU(pcCU, Vis_Image);
    ImgMatrix.pushImg(Vis_Image, "Current CU");

//    getVis_YUVBuffer(pcCU, pcOrgYuv, "getVis_YUVBuffer ORG", Vis_Image, Vis_Text);
//    ImgMatrix.pushImg(Vis_Image, "YUV ORG");

//    getVis_YUVBuffer(pcCU, pcPredYuv, "getVis_YUVBuffer PRED", Vis_Image, Vis_Text);
//    ImgMatrix.pushImg(Vis_Image, "YUV PRED");

    //PRED BUFFER
    getVis_SingleYUVBuffers(pcCU, pcPredYuv, Y, U, V, false); //no rescale!
    ImgMatrix.pushImg(Y, "PRED Y");
    ImgMatrix.pushImg(U, "PRED U");
    ImgMatrix.pushImg(V, "PRED V");

    //RESI BUFFER
    getVis_SingleYUVBuffers(pcCU, rpcResiYuv, Y, U, V, true);
    ImgMatrix.pushImg(Y, "RESI Y");
    ImgMatrix.pushImg(U, "RESI U");
    ImgMatrix.pushImg(V, "RESI V");

    //RESIBEST BUFFER
    getVis_SingleYUVBuffers(pcCU, rpcResiBestYuv, Y, U, V, true);
    ImgMatrix.pushImg(Y, "RESIBEST Y");

    //REC BUFFER
    getVis_YUVBuffer(pcCU, rpcRecYuv, "getVis_YUVBuffer REC", Vis_Image, Vis_Text);
    ImgMatrix.pushImg(Vis_Image, "REC");

//    if(Global.CurrentCTU == 16)
//    {
//      Mat Y, U, V;
//      copy_internal_yuv(HM_2_MAT, rpcResiYuv, Y, Rect(), TEXT_LUMA);
//      copy_internal_yuv(HM_2_MAT, rpcResiYuv, U, Rect(), TEXT_CHROMA_U);
//      copy_internal_yuv(HM_2_MAT, rpcResiYuv, V, Rect(), TEXT_CHROMA_V);
//
//      QString FN = QString("images/POC%1_CTU%2_%3_Depth%4")
//          .arg(Global.CurrentPOC).arg(Global.CurrentCTU).arg(PartitionSizeStrings[ePartSize]).arg(pcCU->getDepth(0));
//      writeJPG_Direkt(Y, (FN + "_Y.png").toStdString());
//      writeJPG_Direkt(U, (FN + "_U.png").toStdString());
//      writeJPG_Direkt(V, (FN + "_V.png").toStdString());
//
//      int a = 0;
//    }
  }

  void createImg_xMotionEstimation(TEncSearch* EncSearch, TComDataCU* pcCU, TComYuv* pcYuvOrg, Int iPartIdx,
                                   RefPicList eRefPicList, TComMv* pcMvPred, Int iRefIdxPred)
  {
    if (not Global.isObsCTU())
      return;

//    if(pcCU->getPic()->getPOC() <= 0) //not interested in INTRA pic
//      return;

    this->ImgMatrix.createEmptyRow("Results xMotionEstimation", BRBA_BLUE);

    //FIXME: BAD HACK!
    assert(0);
    int AbsPartIdx = pcCU->getZorderIdxInCU(); //AbsPart is ALWAYS ZOrder
    sCU CU = get_CU_FIN(pcCU, AbsPartIdx); //LIKELY WRONG: need get_CU_RDO()

    //---------------------------------------------
    // HERE WE GO! LET'S DO SOMETHING WITH THE DATA
    //---------------------------------------------

    //Getting original pixel values of LCU
    Mat PicYuvOrg;
    copy_PicYuv2Mat(pcCU->getPic()->getPicYuvOrg(), PicYuvOrg, INTER_NEAREST);
    convertToCV_8UC3(PicYuvOrg);
    Mat PicYuvOrgROI = PicYuvOrg(Rect(CU.CTUPos.x, CU.CTUPos.y, CTU_DIM, CTU_DIM));
    Mat LCU_Final;
    cvtColor(PicYuvOrgROI, LCU_Final, CV_YCrCb2RGB);

    Mat TinyROI = LCU_Final(Rect(CU.RelPos.x, CU.RelPos.y, CU.Width, CU.Width));

    //Let's decide on a color, color-fanboy!
    Scalar color(128,128,128); //grey
    if(pcCU->getPredictionMode(0) == MODE_INTRA)
      color = Scalar(0,0,255); // red
    else if(pcCU->getPredictionMode(0) == MODE_INTER && pcCU->isSkipped(0))
      color = Scalar(0,255,0); // green
    else if(pcCU->getPredictionMode(0) == MODE_INTER)
      color = Scalar(255,0,0); // blue

    //Coloring ROI
    TinyROI = color;

    PartSize ePartSize = pcCU->getPartitionSize(0);

    //create InfoImg
    Mat InfoImg(VIS_TEXT_SIZE, CV_8UC3, Scalar(128,128,128));
    QString Info = QString("createImg_xMotionEstimation()\n");
    Info += getString_GeneralInfo(pcCU, iPartIdx);
    Info += getString_xMotionEstimation(EncSearch, pcCU, pcYuvOrg, iPartIdx, eRefPicList, pcMvPred, iRefIdxPred);
    writeText(InfoImg, Info, 2.0);

    //Writing jpg
    ImgMatrix.pushImg(LCU_Final, "xMotionEstimation");
    //ImgMatrix.setImg(1, LCU_Final.clone());
    ImgMatrix.pushImg(InfoImg, "xMotionEstimation");

  }

  QString getString_xMotionEstimation(TEncSearch* EncSearch, TComDataCU* pcCU, TComYuv* pcYuvOrg, Int iPartIdx,
                                             RefPicList eRefPicList, TComMv* pcMvPred, Int iRefIdxPred)
  {
    QString Info;
    Info += QString("MV-search-range=%1 \n")
                     .arg(EncSearch->m_aaiAdaptSR[eRefPicList][iRefIdxPred]);
    return Info;

  }

};

