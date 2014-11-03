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


#include "CGlobal.h"
#include "CShow.h"
#include "HARP_Defines.h"

#ifdef ACTIVATE_CALLGRIND
#include <valgrind/callgrind.h>


using namespace std;
using namespace cv;

inline void CG_startCallGraph()
{
#ifdef CG_CALLGRAPH_INTER_ONLY
		if (Global.CurrentPOC == 0)
			return;
#endif
	cout << "STARTING CALLGRIND INSTRUMENTATION" << endl;
	CALLGRIND_START_INSTRUMENTATION;

}

inline void CG_stopCallGraph()
{
#ifdef CG_CALLGRAPH_INTER_ONLY
		if (Global.CurrentPOC == 0)
			return;
#endif
	  cout << "STOPPING CALLGRIND INSTRUMENTATION" << endl;
	  CALLGRIND_STOP_INSTRUMENTATION;
	  CALLGRIND_DUMP_STATS;
}

inline void CG_startHeatmap()
{
  assert(0); //TODO: We need to replace the OTab output
	CALLGRIND_START_INSTRUMENTATION;
}

inline void CG_stopHeatmap(TComDataCU* rpcTempCU)
{
	//cout << "STOPPING CALLGRIND INSTRUMENTATION" << endl;
	cout << "#" << flush;
	CALLGRIND_STOP_INSTRUMENTATION;
	CALLGRIND_DUMP_STATS;

	//-------------------------------
	// FIND GENERATED CALLGRIND.OUT.X
	//-------------------------------
	QString TmpDir = QString::fromStdString(Global.TmpDir);
	system("sync"); //FIXME: may not be necessary
	QStringList nameFilter(QString("callgrind.out.*"));
	QDir directory(TmpDir); //working directory
	QStringList Entries = directory.entryList(nameFilter);

	//-------------------------------
	// HIGHLANDER INSISTS TO BE THE ONLY ONE
	//-------------------------------
	bool safetyCheck = false; //need to disable this for GDB debugging
	if (safetyCheck)
	{
		if(Entries.size() == 0)
		  THROW_ERROR("callgrind.out.* file missing");
		if(Entries.size() > 1)
		  THROW_ERROR("Too many callgrind.out.* files");
	}

	//-------------------------------
	// CALLING CALLGRIND_ANNOTATE
	//-------------------------------
	QString CallgrindAnnotateStdout;
	QString CallgrindAnnotateStderr;
	if(Entries.size() >= 1) //DEBUG
	{
		QString SourceFN = TmpDir + Entries.at(0);
		QString Call = QString("callgrind_annotate %1 --threshold=95").arg(SourceFN);

		QProcess Process;
		Process.start(Call);
		Process.waitForFinished(-1);
		CallgrindAnnotateStdout = Process.readAllStandardOutput();
		CallgrindAnnotateStderr = Process.readAllStandardError();
		if(CallgrindAnnotateStderr.length() != 0)
			THROW_ERROR("callgrind_annotate error: " + CallgrindAnnotateStderr.toStdString());
		QFile::remove(SourceFN); //delete the callgrind.out.* file
	}

	//-------------------------------
	// PTOOLS CU PYTON EXPORT
	//-------------------------------
	assert(0);
	//FIXME!
//	sCU CU = get_CU_RDO(rpcTempCU);
//	assert(rpcTempCU->getAddr() == CU.CTUIdx);
//	OTab PyCU = dictionize_CU_PTOOLS(CU);
//	PyCU["Callgrind"] = CallgrindAnnotateStdout.toStdString();
//
//	char PKL_FN[500]; //uniquely identifies our CU
//	sprintf(PKL_FN, "%sCG_POC%05d_CTU%05d_RastPartIdx%04d_Width%03d.pkl", Global.TmpDir.c_str(), CU.POC, CU.CTUIdx, CU.RastPartIdx, CU.Width);
//	save_CU(PyCU, PKL_FN);
}


//	QFile::remove(SourceFN);
//	QFile::remove(TargetFN);

//	//-------------------------------
//	// PREPARE: CALLGRIND_ANNOTATE CALL
//	//-------------------------------
//    char CU_Passport[500]; //uniquely identifies our CU
//    sprintf(CU_Passport, "POC%05d_CTU%05d_RastPartIdx%04d_Width%03d", CU.POC, CU.IdxLCU, CU.RastPartIdx, CU.Width);
//    QString SourceFN = TmpDir + Entries.at(0);
//    QString TargetFN = QString("%1callgrind_annotate_%2").arg(TmpDir).arg(CU_Passport);
//
//    if(QFile::exists(TargetFN)) //hm?? it seems we already did this file
//      cout << "WARNING: " << TargetFN.toStdString() << " exists, will be overwritten" << endl;
//
//	//-------------------------------
//	// CALL: CALLGRIND_ANNOTATE
//	//-------------------------------
//	char call[500];
//	QString Call = QString("callgrind_annotate %1 --threshold=95 > %2").arg(SourceFN).arg(TargetFN);
//	system(Call.toStdString().c_str());
//	cout << "Created: " << TargetFN.toStdString() << endl;
//	QFile::remove(SourceFN);

#endif
