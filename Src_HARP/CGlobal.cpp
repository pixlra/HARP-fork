// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#include "CGlobal.h"
#include "PyHelper.h"

    CGlobal::CGlobal()
    {
    	pyf_initialize();
    	Converter = new NDArrayConverter;

      //---------------------------------------------
      // DEFAULT VALUES
      //---------------------------------------------
    	TmpDir = "tmp/"; //CAREFULL, gets deleted, make sure it ends with "/"!
      CurrentCTU = -1;  //encoder continually places current CTU index here
      CurrentPOC = 0;  //encoder continually places current POC index here
      initDone = false;

		assert(HARP_ObsPOCs.size() == 0);
		assert(HARP_ObsCTUs.size() == 0);
    }

    CGlobal::~CGlobal()
    {
    	pyf_finalize();
    }

    //IMPORTANT NOTE:: init() MUST be called INSTANTLY
    //AFTER all cmd line options have been parsed
    void CGlobal::init()
    {
		if(initDone)
		  THROW_ERROR("CGlobal: multiple initialization attempted");

#ifdef ACTIVATE_HARP
#ifdef ACTIVATE_HARPGUI
		//GUI
		int argc = 2;
		char* argv[] ={strdup("program"),strdup("first-argument")};

		App =	new QApplication(argc, &argv[0]);
		HarpGUI = new CHarpGUI;
		HarpGUI->show();
#endif
#endif

		//INIT TMP DIR
		if(not HARP_RateCurves)
			initTmpDir();

		//cout << "Global.init() done" << endl;
		initDone = true;
    }

    //INITIALIZING TMP DIRECTORY FOR EACH DEBUG RUN
    void CGlobal::initTmpDir()
    {
    	static bool FirstCall = true;
    	if (FirstCall)
    	{
//    		if(this->HARP_CleanTmpDir)
//    		{
//    			system((string ("rm -rf ") + this->TmpDir).c_str());
//    			cout << "HARP TmpDir cleaned\n";
//    		}

    		system((string ("mkdir -p ") + this->TmpDir).c_str());

    		FirstCall = false;
    	}
    }

    void CGlobal::printVersion()
    {
    	printf("===================== HARP =========================\n");
    	printf("================= Version %s =====================\n", HARP_VERSION);
    	printf("====================================================\n");
#ifdef ACTIVATE_NEXT
    	cout << "WARNING: NEXT development branch is active!" << endl << endl;
#endif
    }

    void CGlobal::printOverview()
    {
    	printf("============= HARP GLOBAL SETTINGS =================\n");
		cout << "Number of observed POCs: " << HARP_ObsPOCs.size() << endl;
		cout << "In detail: ";
		for(vector<int>::iterator it = HARP_ObsPOCs.begin(); it != HARP_ObsPOCs.end(); ++it)
		{
			cout << *it << " ";
			if(*it == -1)
				cout << " (= all POCs) ";
		}
		cout << endl;
		cout << "\nNumber of observed CTUs: " << HARP_ObsCTUs.size() << endl;
		cout << "In detail: ";
		for(vector<int>::iterator it = HARP_ObsCTUs.begin(); it != HARP_ObsCTUs.end(); ++it)
		{
			cout << *it << " ";
			if(*it == -1)
				cout << " (= all CTUs) ";
		}
		cout << endl;
		cout << "FN_InputYUV: "    << FN_InputYUV.toLocal8Bit().constData() << endl << endl;

		const char *OnOff[] = {"off", "on"};

		cout << "HARP command line switches:" << endl;
		cout << "HARP_RateCurves: \t" 	<< OnOff[HARP_RateCurves] << endl;
		cout << "HARP_RDO: \t\t" 			<< OnOff[HARP_RDO] << endl;
		cout << "HARP_PUs: \t\t" 			<< OnOff[HARP_PUs] << endl;
		cout << "HARP_TUs: \t\t" 			<< OnOff[HARP_TUs] << endl;
		cout << "HARP_RefIndices: \t"   << OnOff[HARP_RefIndices] << endl;
		cout << "HARP_UnitCloseup: \t"  << OnOff[HARP_UnitCloseup] << endl;
		cout << "HARP_TmpDir: \t\t"     << this->TmpDir << endl;
		cout << "HARP_CG_Callgraph: \t"  << OnOff[HARP_CG_Callgraph] << endl;
		cout << "HARP_CG_Heatmap: \t"    << OnOff[HARP_CG_Heatmap] << endl;

		printf("====================================================\n");
    }

    void CGlobal::setCurrentPOC(int POC)
    {
      this->CurrentPOC = POC;
    }

    int CGlobal::getCurrentPOC()
    {
      return this->CurrentPOC;
    }

    void CGlobal::setCurrentCTU(int CTU)
    {
      QCoreApplication::processEvents();
      this->CurrentCTU = CTU;
    }

    int CGlobal::getCurrentCTU()
    {
      return this->CurrentCTU;
    }

    bool CGlobal::isObsPOC()
    {
#ifndef ACTIVATE_HARP
    	return 0;
#endif

    	if (not initDone)
    		THROW_ERROR("CGlobal: missing initialization");

		if(HARP_ObsPOCs.size() == 0)
			return true; //cout << "WARNING: No HARP_ObsPOCs specified" << endl;

		for(vector<int>::iterator it = HARP_ObsPOCs.begin(); it != HARP_ObsPOCs.end(); ++it)
		{
			int value = *it;
			if(CurrentPOC== *it)
				return true;
			if(*it == -1) //every POC is interesting
			  return true;
		}
		return false;
    }

    bool CGlobal::isObsCTU()
    {


		if (not isObsPOC())
			return false;

    	//HACK
    	//return true;

		//look if current CTU index is interesting
		for(vector<int>::iterator it = HARP_ObsCTUs.begin(); it != HARP_ObsCTUs.end(); ++it)
		{
			int value = *it;
			if(CurrentCTU == *it)
			  return true;
			if(*it == -1) //every CTU is interesting
			  return true;
		}

		return false;
    }

    void CGlobal::exportImage(Mat Image, string nickname, bool withPOCIdx, bool withCTUIdx)
    {
		char POCStr[500] = "";
		char CTUStr[500] = "";
		if(withPOCIdx)
			sprintf(POCStr, "POC%05d_", this->getCurrentPOC());
		if(withCTUIdx)
			sprintf(CTUStr, "_CTU%04d", this->getCurrentCTU());

		string FN = this->TmpDir + POCStr + nickname + CTUStr + IMAGE_FORMAT;

		//format given by provided filename!
		int Quality = JPG_QUALITY; //100 = best
		vector<int> params;
		params.push_back(CV_IMWRITE_JPEG_QUALITY);
		params.push_back(Quality);

		//INVERTING
		if (IS_INVERTING)
			Image = invertImage(Image);

		imwrite(FN.c_str(), Image, params);
		cout << "Exported: " << FN << endl;
    }
