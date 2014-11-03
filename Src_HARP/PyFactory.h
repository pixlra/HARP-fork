// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include "TLibCommon/TypeDef.h"

#include "HARP_Defines.h"
#include "CHelper.h"
#include "CShow.h"

#include "PyNDArray.h"
#include "CGlobal.h"
#include "PyHelper.h"

//------------------------------------------------------------------------------
//  CONVERSION YUV <-> NUMPY
//------------------------------------------------------------------------------
inline PyObject* convert_PicYuv2Py(TComPicYuv* pcPicYuv, int Channel)
{
	int Margin, Stride, Width, Height;
	Pel* Src;

	if(Channel == TEXT_LUMA)
	{
		Margin = pcPicYuv->getLumaMargin();
		Width =  pcPicYuv->getWidth();
		Height =  pcPicYuv->getHeight();
		Src = pcPicYuv->getBufY();
		Stride = pcPicYuv->getStride();
	}
	else  //CHROMA
	{
		Margin = pcPicYuv->getChromaMargin();
		Width =  pcPicYuv->getWidth() / 2;
		Height =  pcPicYuv->getHeight() / 2;
		Stride = Width + (pcPicYuv->getChromaMargin() * 2);
		if(Channel == TEXT_CHROMA_U)
			Src = pcPicYuv->getBufU();
		else if (Channel == TEXT_CHROMA_V)
			Src = pcPicYuv->getBufV();
		else assert(0);
	}
	Src += Margin + Margin*Stride; //getting rid of first margin in the upper left

	npy_intp dimarray[2] = {Height, Width};
	PyObject* poDst = PyArray_SimpleNew(2, dimarray, NPY_SHORT);
	Pel* Dst = (Pel*) PyArray_DATA(poDst);

    for (int y = 0; y < Height; y++)
    {
      ::memcpy(Dst, Src, sizeof(Pel) * Width);
      Src += Stride;
      Dst += Width;
    }

    return poDst;
}

inline PyObject* convert_Yuv2Py_Luminance(TComYuv* pcYuv)
{
    int Height  = pcYuv->getHeight();
    int Width   = pcYuv->getWidth();
    int Stride  = pcYuv->getStride();
    Pel *Src  = pcYuv->getLumaAddr();

	npy_intp dimarray[2] = {Width, Height};
	PyObject* poDst = PyArray_SimpleNew(2, dimarray, NPY_SHORT);
	Pel* Dst = (Pel*) PyArray_DATA(poDst);

	const npy_intp* _strides = PyArray_STRIDES(poDst);
	int stride_y = _strides[0];
	int stride_x = _strides[1];

    for (int y = 0; y < Height; y++)
    {
      ::memcpy(Dst, Src, sizeof(Pel) * Width);
      Src += Stride;
      Dst += Width;
    }

    return poDst;
}

inline void convert_Py2Yuv_Luminance(PyObject* poSrc, TComYuv* pcYuv)
{
    assert (PyArray_TYPE(poSrc) == NPY_SHORT);
    assert (PyArray_NDIM(poSrc) == 2);
    const npy_intp* _sizes   = PyArray_DIMS(poSrc);
    const npy_intp* _strides = PyArray_STRIDES(poSrc);
	int stride_y = _strides[0];
	int stride_x = _strides[1];

    int Height  = pcYuv->getHeight();
    int Width   = pcYuv->getWidth();
    int Stride  = pcYuv->getStride();
    Pel *Dst  = pcYuv->getLumaAddr();
    assert(Height == _sizes[0]);
    assert(Width  == _sizes[1]);

    //TODO: safety checks
	Pel* Src = (Pel*) PyArray_DATA(poSrc);

    for (int y = 0; y < Height; y++)
    {
      ::memcpy(Dst, Src, sizeof(Pel) * Width);
      Dst += Stride;
      Src += Width;
    }
}

inline void convert_Py2Yuv_Luminance_Part(PyObject* poSrc, TComYuv* pcYuv, UInt uiPartAddr, UInt Width, UInt Height)
{
    assert (PyArray_TYPE(poSrc) == NPY_SHORT);
    assert (PyArray_NDIM(poSrc) == 2);
    const npy_intp* _sizes   = PyArray_DIMS(poSrc);
    const npy_intp* _strides = PyArray_STRIDES(poSrc);

    int Stride = pcYuv->getStride();
    Pel *Dst   = pcYuv->getLumaAddr(uiPartAddr);
    assert(Height == _sizes[0]);
    assert(Width  == _sizes[1]);

    //TODO: safety checks
	Pel* Src = (Pel*) PyArray_DATA(poSrc);

    for (int y = 0; y < Height; y++)
    {
      ::memcpy(Dst, Src, sizeof(Pel) * Width);
      Dst += Stride;
      Src += Width;
    }
}

//Void TComYuv::copyPartToPartLuma  ( TComYuv* pcYuvDst, UInt uiPartIdx, UInt iWidth, UInt iHeight )
//{
//  Pel* pSrc =           getLumaAddr(uiPartIdx);
//  Pel* pDst = pcYuvDst->getLumaAddr(uiPartIdx);
//  if( pSrc == pDst )
//  {
//    //th not a good idea
//    //th best would be to fix the caller
//    return ;
//  }
//
//  UInt  iSrcStride = getStride();
//  UInt  iDstStride = pcYuvDst->getStride();
//  for ( UInt y = iHeight; y != 0; y-- )
//  {
//    ::memcpy( pDst, pSrc, iWidth * sizeof(Pel) );
//    pSrc += iSrcStride;
//    pDst += iDstStride;
//  }
//}



//------------------------------------------------------------------------------
//  PIC Sample Buffer
//------------------------------------------------------------------------------
inline PyObject* pyf_create_PIC( TComPicYuv* pcPicYuv )
{
	PyObject* PoDict = PyDict_New();

	PyObject* poY = convert_PicYuv2Py(pcPicYuv, TEXT_LUMA);
	PyObject* poU = convert_PicYuv2Py(pcPicYuv, TEXT_CHROMA_U);
	PyObject* poV = convert_PicYuv2Py(pcPicYuv, TEXT_CHROMA_V);
	PyDict_SetItem(PoDict, PyString_FromString("Y"), poY);
	PyDict_SetItem(PoDict, PyString_FromString("U"), poU);
	PyDict_SetItem(PoDict, PyString_FromString("V"), poV);

	Py_DECREF(poY);
	Py_DECREF(poU);
	Py_DECREF(poV);

	return PoDict;
}

//------------------------------------------------------------------------------
//  POC
//------------------------------------------------------------------------------
inline PyObject* pyf_create_POC( TComPic* rpcPic, int SliceIdx, bool withRefList )
{
	assert(SliceIdx == 0);

	//welcome to this world!
	PyObject* PoDict = PyDict_New();

	//HM interfacing
	UInt Width_inCTUs  = rpcPic->getPicSym()->getFrameWidthInCU();
	UInt Height_inCTUs = rpcPic->getPicSym()->getFrameHeightInCU();
	TComPicYuv* YuvRec = rpcPic->getPicYuvRec(); //YuvRec because we may be on decoder side, also
	int DimX = YuvRec->getWidth();
	int DimY = YuvRec->getHeight();
	int POC = rpcPic->getPOC();

	//Object name
	PyDict_SetItemString(PoDict, "Name", PyString_FromString("POC"));

	//POCIdx
	PyDict_SetItemString(PoDict, "Idx", PyInt_FromLong(POC));

	//Size in CTUs
	PyObject *PoTuple1 = pyf_getTuple(Width_inCTUs, Height_inCTUs);
	PyDict_SetItem(PoDict, PyString_FromString("Size_inCTUs"), PoTuple1);
	Py_DECREF(PoTuple1);

	//Size
	PyObject *PoTuple2 = pyf_getTuple(DimX, DimY);
	PyDict_SetItem(PoDict, PyString_FromString("Size"), PoTuple2);
	Py_DECREF(PoTuple2);

	if (Global.isEncoder)
	{
    //YuvOrg
    PyObject* poYuvOrg = pyf_create_PIC(rpcPic->getPicYuvOrg());
    PyDict_SetItem(PoDict, PyString_FromString("YuvOrg"), poYuvOrg);
    Py_DECREF(poYuvOrg);
	}

	//IMPORTANT NOTE:
	// pyf_create_POC() may be called for current POC and also(!) for RefPOCs
	// if we are doing a RefPOC, YuvRec is valid (finished already)
	// if we are doing CurPOC, YuvRec is not yet ready here!
	// solution: YuvRec will be overwritten at end of compressSlice()!

	//YuvRec
	PyObject* poYuvRec = pyf_create_PIC(rpcPic->getPicYuvRec());
	PyDict_SetItem(PoDict, PyString_FromString("YuvRec"), poYuvRec);
	Py_DECREF(poYuvRec);

	//Ref POCs, LIST0
	if (withRefList)
	{
		PyObject *poRefList0 = PyList_New(0);
		PyDict_SetItem(PoDict, PyString_FromString("List0_Refs"), poRefList0);
		Py_DECREF(poRefList0);
		TComSlice* pcSlice = rpcPic->getSlice(SliceIdx);
		int NumRefFrames =  pcSlice->getNumRefIdx(REF_PIC_LIST_0);
		for(int i = 0; i < NumRefFrames; i++)
		{
			TComPic* pcPic_ref = pcSlice->getRefPic(REF_PIC_LIST_0, i);
			PyObject *poRefPOC = pyf_create_POC(pcPic_ref, 0, false);
			PyList_Append(poRefList0, poRefPOC);
			Py_DECREF(poRefPOC);
		}
	}

	//List of CTUs
	Global.PyList_CTUs = PyList_New(0);
	PyDict_SetItem(PoDict, PyString_FromString("CTUs"), Global.PyList_CTUs);
	Py_DECREF(Global.PyList_CTUs);

	return PoDict;
}

//------------------------------------------------------------------------------
//  CTU
//------------------------------------------------------------------------------
inline PyObject* pyf_create_CTU(TComDataCU* pcCU)
{
	//welcome to this world!
	PyObject* PoDict = PyDict_New();

	//HM interfacing
	TComPic* rpcPic = pcCU->getPic();
	UInt Width_inCTUs  = rpcPic->getPicSym()->getFrameWidthInCU();
	UInt Height_inCTUs = rpcPic->getPicSym()->getFrameHeightInCU();
	int CTUIdx  = pcCU->getAddr();
	int Width   = CTU_DIM;
	int CTUPosx = (CTUIdx % Width_inCTUs) * CTU_DIM;
	int CTUPosy = (CTUIdx / Width_inCTUs) * CTU_DIM;

	//Object name
	PyDict_SetItemString(PoDict, "Name", PyString_FromString("CTU"));

	//CTU Idx
	//PyDict_SetItem(PoDict, PyString_FromString("CTUIdx"), PyInt_FromLong(CTUIdx));
	PyDict_SetItemString(PoDict, "Idx", PyInt_FromLong(CTUIdx));

	//CTU Size
	PyObject *PoTuple1 = pyf_getTuple(Width, Width);
	PyDict_SetItemString(PoDict, "Size", PoTuple1);
	Py_DECREF(PoTuple1);

	//CTU Anchor
	PyObject *PoTuple2 = pyf_getTuple(CTUPosx, CTUPosy);
	PyDict_SetItemString(PoDict, "Pos", PoTuple2);
	Py_DECREF(PoTuple2);

  //List of RDO_CUs
  Global.PyList_RDO_CUs = PyList_New(0); //keep a pointer to this goodie


  //HACK: disabled
  //PyDict_SetItemString(PoDict, "RDO_CUs", Global.PyList_RDO_CUs);
  //Py_DECREF(Global.PyList_RDO_CUs);

	//List of CUs
	Global.PyList_FIN_CUs = PyList_New(0); //keep a pointer to this goodie
	PyDict_SetItemString(PoDict, "CUs", Global.PyList_FIN_CUs);
	Py_DECREF(Global.PyList_FIN_CUs);

	return PoDict;
}

//------------------------------------------------------------------------------
//  CU
//------------------------------------------------------------------------------
inline PyObject* pyf_create_CU_internal(sCU &CU);

inline PyObject* pyf_create_CU_RDO(TComDataCU* pcCU)//, TComYuv *OrgYuv)
{
  sCU CU = get_CU_RDO(pcCU);
  return pyf_create_CU_internal(CU);
}

inline PyObject* pyf_create_CU_FIN(TComDataCU* pcCU, UInt AbsPartIdx)
{
  sCU CU = get_CU_FIN(pcCU, AbsPartIdx);
  return pyf_create_CU_internal(CU);
}

inline PyObject* pyf_create_CU_internal(sCU &CU)
{

	// create dictionary
	PyObject* PoDict = PyDict_New();

	// Object name
	PyDict_SetItemString(PoDict, "Name", PyString_FromString("CU"));

	// POC, CTU info
//	PyDict_SetItem(PoDict, PyString_FromString("POCIdx"), PyInt_FromLong(CU.POC));
//	PyDict_SetItem(PoDict, PyString_FromString("CTUIdx"), PyInt_FromLong(CU.CTUIdx));

	// CU position in frame
	PyObject *PoTuple = pyf_getTuple(CU.Pos.x, CU.Pos.y);
	PyDict_SetItem(PoDict, PyString_FromString("Pos"), PoTuple);
	Py_DECREF(PoTuple);

	// CU Size
	PyObject *PoTuple1 = pyf_getTuple(CU.Width, CU.Width);
	PyDict_SetItemString(PoDict, "Size", PoTuple1);
	Py_DECREF(PoTuple1);

	// Depth
	PyDict_SetItem(PoDict, PyString_FromString("Depth"), PyInt_FromLong(CU.Depth));

	// CU abs/raster partition indices
	PyDict_SetItem(PoDict, PyString_FromString("AbsPartIdx"), PyInt_FromLong(CU.AbsPartIdx));
	PyDict_SetItem(PoDict, PyString_FromString("RastPartIdx"), PyInt_FromLong(CU.RastPartIdx));

	// Mode
	PyDict_SetItemString(PoDict, "Mode", PyString_FromString(CU.Mode.c_str()));

	// List of PUs
	Global.PyList_PUs = PyList_New(0); //keep a pointer to this goodie
	PyDict_SetItemString(PoDict, "PUs", Global.PyList_PUs);
	Py_DECREF(Global.PyList_PUs);



	// Uncommented, OrgYuv pointer only available for RDO_CU

//	// YuvOrg CU Patch
//	PyObject*  poOrgYuv = convert_Yuv2Py_Luminance(OrgYuv);
//	PyDict_SetItem(PoDict, PyString_FromString("Y_Org_Patch"), poOrgYuv);
//	Py_DECREF(poOrgYuv);

//	PyObject *pFunc = pyf_getFuncHandle("test_retval", "a_teste_xMotionEstimation"); // LOAD MODULE + FUNCTION
//	PyObject *test = pyf_callFunc_Arg1(pFunc, poOrgYuv); // CALL FUNCTION
//	Py_XDECREF(pFunc); // CLEAN UP
//	Py_XDECREF(test);

	// CONVERT YUVORG TO NUMPY, PROCESS, THEN CONVERT BACK, CHECKSUMS
//	float sum = sumAllPelsY(OrgYuv);
//	printf("Sum1: %f\n", sum);

//	Mat Vis_Image1;
//	copy_internal_yuv(HM_2_MAT, OrgYuv, Vis_Image1, Rect(), TEXT_LUMA);
//	convertToCV_8UC3(Vis_Image1);
//	writeJPG_Direkt(Vis_Image1, "Test1.png");

//	PyObject *pFunc = pyf_getFuncHandle("test_retval", "a_teste_xMotionEstimation"); // LOAD MODULE + FUNCTION
//	PyObject *test = pyf_callFunc_Arg1(pFunc, poOrgYuv); // CALL FUNCTION
//	Py_XDECREF(pFunc); // CLEAN UP

//	convert2Yuv_Y(test, OrgYuv);
//
//	//copy_Yuv2Mat(OrgYuv, Vis_Image, INTER_NEAREST);
//	Mat Vis_Image2;
//	copy_internal_yuv(HM_2_MAT, OrgYuv, Vis_Image2, Rect(), TEXT_LUMA);
//	convertToCV_8UC3(Vis_Image2);
//	writeJPG_Direkt(Vis_Image2, "Test2.png");
//	//cvtColor(Vis_Image, Vis_Image, CV_YCrCb2RGB);
//
//	sum = sumAllPelsY(OrgYuv);
//	printf("Sum2: %f\n", sum);

//	Py_XDECREF(test);

	return PoDict;
}

//------------------------------------------------------------------------------
//  PU
//------------------------------------------------------------------------------
inline PyObject* pyf_create_PU_internal(sPU &PU, bool withMEs);

inline PyObject* pyf_create_PU_RDO(TComDataCU* pcCU, Int iPartIdx)
{
  sCU CU = get_CU_RDO(pcCU);
  sPU PU;
  PU.CU = CU;

  //HM Interfacing
  UInt  uiPartAddr;
  Int   PU_Width, PU_Height;
  pcCU->getPartIndexAndSize( iPartIdx, uiPartAddr, PU_Width, PU_Height );
  UInt AbsPartIdx    = pcCU->getZorderIdxInCU();
  int RasterPartIdx  = g_auiZscanToRaster[AbsPartIdx+uiPartAddr];
  int SUnitsPerRow = CTU_DIM/4; // 64/4 = 16 StorageUnits in a CTB row

  PU.Pos  = PU.CU.CTUPos + getRelPos(RasterPartIdx);
  PU.Size = Point(PU_Width , PU_Height );
  PU.AbsPartIdx  = AbsPartIdx+uiPartAddr;
  PU.RastPartIdx = RasterPartIdx;

  return pyf_create_PU_internal(PU, true);
}

inline PyObject* pyf_create_PU_FIN(TComDataCU* pcCU, UInt iPartIdx, UInt AbsPartIdx, UInt Depth )
{
  sCU CU = get_CU_FIN(pcCU, AbsPartIdx);
  sPU PU;
  PU.CU = CU;

  UInt uiPartAddr;
  Int PU_Width,  PU_Height;
  myGetPartIndexAndSize( pcCU, AbsPartIdx, Depth, iPartIdx, //uiPartIdx = PUIdx: PU index, maybe just one, maybe up to four
                         uiPartAddr, PU_Width, PU_Height ); //ruiPartAddr is the same as the above uiSubPartIdx


  int RasterPartIdx  = g_auiZscanToRaster[AbsPartIdx+uiPartAddr];
  int SUnitsPerRow = 64/4; // 64/4 = 16 StorageUnits in a CTU row

  PU.Pos  = PU.CU.CTUPos + getRelPos(RasterPartIdx);
  PU.Size = Point(PU_Width , PU_Height );
  PU.AbsPartIdx  = AbsPartIdx+uiPartAddr;
  PU.RastPartIdx = RasterPartIdx;

  return pyf_create_PU_internal(PU, false);
}

inline PyObject* pyf_create_PU_internal(sPU &PU, bool withMEs)
{
	// create dictionary
	PyObject* PoDict = PyDict_New();

	//Object name
	PyDict_SetItemString(PoDict, "Name", PyString_FromString("PU"));

	//PU pos
	PyObject *PoTuple3 = pyf_getTuple(PU.Pos.x, PU.Pos.y);
	PyDict_SetItem(PoDict, PyString_FromString("Pos"), PoTuple3);
	Py_DECREF(PoTuple3);

	//PU size
	PyObject *PoTuple4 = pyf_getTuple(PU.Size.x, PU.Size.y);
	PyDict_SetItem(PoDict, PyString_FromString("Size"), PoTuple4);
	Py_DECREF(PoTuple4);

	// PU abs/raster partition indices
	PyDict_SetItem(PoDict, PyString_FromString("AbsPartIdx"), PyInt_FromLong(PU.AbsPartIdx));
	PyDict_SetItem(PoDict, PyString_FromString("RastPartIdx"), PyInt_FromLong(PU.RastPartIdx));

  //List of MEs
	if (withMEs)
	{
    Global.PyList_MEs = PyList_New(0);
    PyDict_SetItem(PoDict, PyString_FromString("MEs"), Global.PyList_MEs);
    Py_DECREF(Global.PyList_MEs); //we handed over responsibility
	}

	return PoDict;
}

//------------------------------------------------------------------------------
//  MEs
//------------------------------------------------------------------------------

inline PyObject* pyf_create_ME(int TypeME, TComDataCU* pcCU, Int iPartIdx, Int iRefIdx)
{
	// create dictionary
	PyObject *PoDict = PyDict_New();

	//Object name
	PyDict_SetItemString(PoDict, "Name", PyString_FromString("ME"));

	if( TypeME == ME_TRANSL)
	  PyDict_SetItemString(PoDict, "Type", PyString_FromString("TRANSL"));

  if( TypeME == ME_AFFINE)
    PyDict_SetItemString(PoDict, "Type", PyString_FromString("AFFINE"));

	//PU Idx
	PyDict_SetItem(PoDict, PyString_FromString("PUIdx"), PyInt_FromLong(iPartIdx));

	//Ref Idx
	PyDict_SetItem(PoDict, PyString_FromString("RefIdx"), PyInt_FromLong(iRefIdx));

	return PoDict;
}

//------------------------------------------------------------------------------
//  APPEND INFO TO ME
//------------------------------------------------------------------------------
inline void pyf_appendto_ME(PyObject* poME,  TComMv _cMVTemp, TComMv _cMvPred, Int _CandIdx,
    UInt _uiMvBits, UInt _uiMvCost, UInt _ruiCost_SADonly, UInt _uiBitsTemp, UInt _uiCostTemp)
{
  //MV (found)
  PyObject *PoTuple = pyf_getTuple(_cMVTemp.getHor(), _cMVTemp.getVer());
  PyDict_SetItem(poME, PyString_FromString("MV_Found"), PoTuple);
  Py_DECREF(PoTuple);

  //MV Predictor
  PyObject *PoTuple2 = pyf_getTuple(_cMvPred.getHor(), _cMvPred.getVer());
  PyDict_SetItem(poME, PyString_FromString("MV_Pred"), PoTuple2);
  Py_DECREF(PoTuple2);

  PyDict_SetItem(poME, PyString_FromString("MV_CandIdx"), PyInt_FromLong(_CandIdx));

  PyDict_SetItem(poME, PyString_FromString("ME_Bits_MVdiff"), PyInt_FromLong(_uiMvBits));
  PyDict_SetItem(poME, PyString_FromString("ME_Cost_MVdiff"), PyInt_FromLong(_uiMvCost));
  PyDict_SetItem(poME, PyString_FromString("ME_Cost_SADonly"), PyInt_FromLong(_ruiCost_SADonly));
  PyDict_SetItem(poME, PyString_FromString("ME_Bits_Final"), PyInt_FromLong(_uiBitsTemp));
  PyDict_SetItem(poME, PyString_FromString("ME_Cost_Final"), PyInt_FromLong(_uiCostTemp));
}

//uniquely identifies our CU
//sprintf(PKL_FN, "%sRDO-CU_POC%05d-Posx%04d-Posy%04d-Width%03d.pkl", Global.TmpDir.c_str(), CU.POC, CU.Pos.x, CU.Pos.y, CU.Width);

