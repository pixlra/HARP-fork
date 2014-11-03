// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include "HARP_Defines.h"
#include "PyFactory.h"

class CPyAppendCUs
{

  PyObject *PyList_FIN_CUs;

public:

  CPyAppendCUs(TComDataCU* pcCU, PyObject *PyList_FIN_CUs)
  {
    if(not Global.isObsPOC())
      return;

    //---------------------------------------------
    // CHANGE HERE
    //---------------------------------------------

    //---------------------------------------------
    this->PyList_FIN_CUs = PyList_FIN_CUs;
    xProcessCU( pcCU, 0, 0);
  };



  void xProcessCU( TComDataCU* pcCU, UInt uiAbsZorderIdx, UInt uiDepth)
  {
    TComPic* pcPic     = pcCU->getPic();
    UInt NumPartInCTU  = pcPic->getNumPartInCU();    //number of StorageUnits (4x4) in CTU
    UInt NumPartInCU = NumPartInCTU >> (uiDepth<<1); //number of StorageUnits (4x4) in current CU
    UInt NextCU_Increment   = NumPartInCU>>2; //increment (in StorageUnits) if CU is splitted further

    //if small block signals: way to go, not deep enough
    if( pcCU->getDepth(uiAbsZorderIdx) > uiDepth ) //if upper left StorageUnit says "Final depth dude!"
    {
      for ( UInt uiPartIdx = 0; uiPartIdx < 4; uiPartIdx++, uiAbsZorderIdx+=NextCU_Increment )
      {
      	//pcCU->getCUPelX() : get absolute pixel index if LCU(!) in frame
        UInt uiLPelX   = pcCU->getCUPelX() + g_auiRasterToPelX[ g_auiZscanToRaster[uiAbsZorderIdx] ];
        UInt uiTPelY   = pcCU->getCUPelY() + g_auiRasterToPelY[ g_auiZscanToRaster[uiAbsZorderIdx] ];
        if(    ( uiLPelX < pcCU->getSlice()->getSPS()->getPicWidthInLumaSamples() )
            && ( uiTPelY < pcCU->getSlice()->getSPS()->getPicHeightInLumaSamples() ) )
        {
          xProcessCU( pcCU, uiAbsZorderIdx, uiDepth+1);
        }
      }
      return;
    }

    //---------------------------------------------
    // WE ARRIVED AT THE FINAL DEPTH FOR THIS CU
    //---------------------------------------------
    sCU CU = get_CU_FIN(pcCU, uiAbsZorderIdx);

    PyObject *PoCU = pyf_create_CU_FIN(pcCU, uiAbsZorderIdx); //,  m_ppcOrigYuv[uiDepth]); //create dictionary
    PyList_Append(PyList_FIN_CUs, PoCU); //append dict to list
    Py_DECREF(PoCU); //list now "owns" the dict
    Global.PyDict_CurCU = PoCU; //keep reference on dict (might come in handy)

    PartSize ePartSize = pcCU->getPartitionSize( uiAbsZorderIdx );
    UInt NumPU = ( ePartSize == SIZE_2Nx2N ? 1 : ( ePartSize == SIZE_NxN ? 4 : 2 ) );
    //NextPU_Increment: increment in terms of StorageUnits
    UInt NextPU_Increment = ( g_auiPUOffset[UInt( ePartSize )] << ( ( pcCU->getSlice()->getSPS()->getMaxCUDepth() - uiDepth ) << 1 ) ) >> 4;

    //----------------------------------------------------
    //  PROCESSING PU'S
    //----------------------------------------------------
    for ( UInt uiPartIdx = 0, uiSubPartIdx = uiAbsZorderIdx; uiPartIdx < NumPU; uiPartIdx++, uiSubPartIdx += NextPU_Increment )
    {
      //----------------------------------------------------
      // GETTING PU SIZES AND COUNT TO NEXT PU (PU OFFSET?)
      //----------------------------------------------------
      UInt ruiPartAddr;
      Int PU_Width,  PU_Height;
      myGetPartIndexAndSize( pcCU, uiAbsZorderIdx, uiDepth, uiPartIdx, //uiPartIdx = PUIdx: PU index, maybe just one, maybe up to four
                             ruiPartAddr, PU_Width, PU_Height ); //ruiPartAddr is the same as the above uiSubPartIdx

      //BUG ALERT! WHY DOES THIS DIFFER? FIXME ASAP!
//      UInt  uiPartAddr2;
//      Int   PU_Width2, PU_Height2;
//      pcCU->getPartIndexAndSize( uiPartIdx, uiPartAddr2, PU_Width2, PU_Height2 );
//      assert(PU_Width == PU_Width2);
//      assert(PU_Height == PU_Height2);
//      assert(ruiPartAddr == uiPartAddr2);

      PyObject *PyList_PUs = PyDict_GetItemString(PoCU, "PUs");

      PyObject *poPU = pyf_create_PU_FIN(pcCU, uiPartIdx, uiAbsZorderIdx, uiDepth); //create dictionary
      PyList_Append(PyList_PUs, poPU); //append dict to list
      Py_DECREF(poPU); //list now "owns" the dict
      Global.PyDict_CurPU = poPU; //keep reference on dict (might come in handy)

      //----------------------------------------------------
      // GETTING MERGE INFO
      //----------------------------------------------------
      bool MergeFlag    = pcCU->getMergeFlag( uiSubPartIdx );
      UInt MergeIndex = pcCU->getMergeIndex(uiSubPartIdx);

      //----------------------------------------------------
      // WE ARE ABLE TO RECONSTRUCT PU ANCHOR IN PIXELS RELATIVE TO THE CTU
      //----------------------------------------------------
      int RasterPartIdx  = g_auiZscanToRaster[uiAbsZorderIdx+ruiPartAddr];
      int SUnitsPerRow = 64/4; // 64/4 = 16 StorageUnits in a CTU row

      Point PU_Anc  = Point(RasterPartIdx % (SUnitsPerRow), RasterPartIdx / (SUnitsPerRow)) * 4;
      Point PU_Dims = Point(PU_Width , PU_Height );
      //Mat PU_Roi = CTU_Roi(Rect(PU_Anc.x, PU_Anc.y, PU_Dims.x, PU_Dims.y));

      //BUG ALERT! WE EXTRACT MVs FOR INTRA ALSO!!

      //----------------------------------------------------
      // WE ARE ABLE TO DETERMINE THE MV OF THIS PU
      //----------------------------------------------------

      if (pcCU->getPredictionMode(uiAbsZorderIdx) != MODE_INTRA)
      {
        TComMv cMv = pcCU->getCUMvField(REF_PIC_LIST_0)->getMv( uiAbsZorderIdx+ruiPartAddr );

        //MV (found)
        PyObject *PoTuple = pyf_getTuple(cMv.getHor(), cMv.getVer());
        PyDict_SetItem(poPU, PyString_FromString("MV"), PoTuple);
        Py_DECREF(PoTuple);
      }

    }
    //off we go to next CU!
  } //end xDrawCU



};
