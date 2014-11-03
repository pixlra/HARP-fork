// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include <sys/time.h>
#include <vector>
#include <iostream>
#include <iterator>
#include <fstream>

#include <vector>
#include <opencv/cv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/features2d/features2d.hpp>

#include <QDir>
#include <QString>
#include <QFileInfo>
#include <QApplication>
#include <QTextEdit>

#include "PyNDArray.h"
#include "HARP_Defines.h"
#include "CHelper.h"


using namespace std;
using namespace cv;

static bool InitDone = false;

// ---------------------------
// GLOBAL, ACCESS FROM ANYWHERE (YES, I KNOW)
// ---------------------------
class CGlobal
{
public:
	// ---------------------------
	// SET BY CMD LINE ARGUMENTS
	// ---------------------------
	bool HARP_RDO; //see paper
	bool HARP_PUs; //see paper
	bool HARP_TUs; //see paper
	bool HARP_RefIndices; //see paper
	bool HARP_UnitCloseup; //see paper
	bool HARP_RateCurves; //for curves: do not clean tmp dir
//	bool HARP_CleanTmpDir; //delete contents of tmp dir at start
	bool HARP_CG_Callgraph; //extract call graphs from encoder run
	bool HARP_CG_Heatmap; //generate RDO heatmaps (use with profileRDO.py script)
	string TmpDir; //CAREFULL, gets deleted, make sure it ends with "/"!
	vector<int> HARP_ObsPOCs;  //set on cmd line
	vector<int> HARP_ObsCTUs;  //set on cmd line

	// ---------------------------
	// PYTHON
	// ---------------------------
	NDArrayConverter *Converter;

	PyObject* PyDict_CurPOC; //root object

	PyObject* PyList_CTUs;
	PyObject* PyDict_CurCTU;

	PyObject* PyList_FIN_CUs;
	PyObject* PyList_RDO_CUs;
	PyObject* PyDict_CurCU;

	PyObject* PyList_PUs;
	PyObject* PyDict_CurPU;

	PyObject* PyList_MEs;
	PyObject* PyDict_CurME;

	// ---------------------------
	// INTERNAL
	// ---------------------------
	bool isEncoder;  //PicYuvOrg is not available on decoder side
	int CurrentCTU;  //encoder continually places current CTU index here
	int CurrentPOC;  //encoder continually places current POC index here
	bool initDone;
	int DimX, DimY;
	int NumCTUs;
	int WidthInLCUs;
	int HeightInLCUs;


	char tmptxt[500];
	QString FN_InputYUV;
	//Tab Cur_PyPOC;
	//Tab DictRDO;
	QApplication *App;

	CGlobal();
	~CGlobal();
	void init();
	void initTmpDir();
	void printVersion();
	void printOverview();
	void setCurrentPOC(int POC);
	int getCurrentPOC();
	void setCurrentCTU(int CTU);
	int getCurrentCTU();
	bool isObsPOC();
	bool isObsCTU();
	void exportImage(Mat Image, string nickname, bool withPOCIdx = false, bool withCTUIdx = false);

};

extern CGlobal Global;
