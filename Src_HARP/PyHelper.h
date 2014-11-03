// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once

#include <Python.h>

#include "HARP_Defines.h"
#include "PyNDArray.h"

//---------------------------------------------
//  HELPER FUNCTIONS
//---------------------------------------------
inline PyObject* pyf_getTuple(int val0, int val1)
{
	PyObject *PoTuple = PyTuple_New(2);
	PyTuple_SetItem(PoTuple, 0, PyInt_FromLong(val0));
	PyTuple_SetItem(PoTuple, 1, PyInt_FromLong(val1));
	return PoTuple;
}

//---------------------------------------------
//  SANITY CHECKS
//---------------------------------------------
static bool pyf_checkPython()
{
	PyObject *ptype, *pvalue, *ptraceback;
	PyErr_Fetch(&ptype, &pvalue, &ptraceback);
	if(ptype != NULL)
	{
		char *pStrErrorMessage = PyString_AsString(pvalue);
		cout << pStrErrorMessage << endl;
		THROW_ERROR("Python error");
	}
	return true;
}


//---------------------------------------------
// PICKLING
//---------------------------------------------
inline void pyf_importModule(string Module)
{
	PyObject * PoMainModule = PyImport_AddModule("__main__");
	PyObject * PoNewModule = PyImport_ImportModule(Module.c_str());
	PyModule_AddObject(PoMainModule, Module.c_str(), PoNewModule);
}

inline PyObject* pyf_declareFunc_pickleObject()
{
	pyf_importModule("pickle");

	// prepare pickling
	PyRun_SimpleString(
	  "def pickleObject(PoDict, FN):\n"
	  "   pickle.dump( PoDict, open(FN, \"wb\" ) )\n"
	  "   return \"Success: wrote \" + FN \n"
	);

	PyObject* PoMainModule = PyImport_AddModule("__main__");
	PyObject* PyfFunc_pickleObject = PyObject_GetAttrString(PoMainModule, "pickleObject");
	return PyfFunc_pickleObject;
}

inline void pyf_callFunc_pickleObject(PyObject * Po, string FN)
{
	static PyObject *PyfFunc_pickleObject = NULL;
	if(PyfFunc_pickleObject == NULL) //yet unitialized
		PyfFunc_pickleObject = pyf_declareFunc_pickleObject(); //one time only, no Py_DECREF

	//write pkl
	PyObject* PoFN = PyString_FromString(FN.c_str());
	PyObject* PoResult =  PyObject_CallFunctionObjArgs(PyfFunc_pickleObject, Po, PoFN, NULL);
	Py_DECREF(PoResult);
	Py_DECREF(PoFN);
	//cout << "#";
	//cout << "Pickled: " << FN << endl;

	// function return string
	std::string resultstr = PyString_AsString(PoResult);
	//cout << resultstr << endl;

	// check for Python errors
	pyf_checkPython();
}

inline PyObject* pyf_getTestArgs()
{
	PyObject *pArgs, *pValue;
	pArgs = PyTuple_New(2);
	for (int i = 0; i < 2; ++i)
	{
		pValue = PyLong_FromLong(i+2);
		if (pValue == NULL)
			THROW_ERROR_PYTHON("Cannot convert argument", "");

		/* pValue reference stolen here: */
		PyTuple_SetItem(pArgs, i, pValue);
	}
	return pArgs;
}

inline PyObject* pyf_getFuncHandle(char* FuncName, char *ModuleName)
{
	PyObject *pModuleName, *pModule, *pFunc;

// WONT WORK, PyImport_AddModule will ADD an empty dict
//pModule = PyImport_AddModule(ModuleName);
//	int size = PyDict_Size(pModule);
//	if (PyDict_Size(pModule) == -1) //not yet imported (module dict is empty)
	{
		//printf("%s not imported yet, importing", ModuleName);

		pModuleName = PyUnicode_FromString(ModuleName);
		pModule = PyImport_Import(pModuleName);
		if(pModule == NULL)
			THROW_ERROR_PYTHON("Module load error", ModuleName);
	}

	pFunc = PyObject_GetAttrString(pModule, FuncName);
	if (pFunc == NULL or PyCallable_Check(pFunc) == 0 )
		THROW_ERROR_PYTHON("Cannot find function", pFunc);


	Py_XDECREF(pModuleName);
	Py_XDECREF(pModule); //multiple imports of the same module are very fast

	return pFunc;
}

inline void pyf_callFunc_ArgsTuple(PyObject *pFunc, PyObject *pArgs)
{
	PyObject *pValue = PyObject_CallObject(pFunc, pArgs);

	if (pValue == NULL)
		THROW_ERROR_PYTHON("Call failed", "");

	printf("Result of call: %ld\n", PyLong_AsLong(pValue));
	Py_DECREF(pValue);
}

inline PyObject* pyf_callFunc_Arg1(PyObject *pFunc, PyObject *pArg1)
{
	PyObject *pValue = PyObject_CallFunctionObjArgs(pFunc, pArg1, NULL);

	if (pValue == NULL)
		THROW_ERROR_PYTHON("Call failed", "");

	//printf("Result of call: %ld\n", PyLong_AsLong(pValue));
	return pValue;  //DONT FORGET TO DECREF!
	//Py_DECREF(pValue);
}

inline void pyf_callTestFunc()
{
	char* FuncName = "multiply";
	char *ModuleName = "a_teste_xMotionEstimation";

	// ARGUMENTS
	PyObject *pArgs = pyf_getTestArgs();

	PyObject *pFunc = pyf_getFuncHandle(FuncName, ModuleName); // LOAD MODULE + FUNCTION
	pyf_callFunc_ArgsTuple(pFunc, pArgs); // CALL FUNCTION
	Py_XDECREF(pFunc); // CLEAN UP FUNC
	Py_DECREF(pArgs);  // CLEAN UP ARGS
}

//---------------------------------------------
// PYTHON INIT
//---------------------------------------------
inline void pyf_initialize()
{
	//TODO: Python safety checks (2.7, sanity check etc.)
	Py_Initialize();


	PyObject *sys = PyImport_ImportModule("sys");
	PyObject *path = PyObject_GetAttrString(sys, "path");
	PyList_Append(path, PyString_FromString("."));
	PyList_Append(path, PyString_FromString("../Next"));

	import_array(); //for numpy support
//	import_array(); //for numpy support

}

//---------------------------------------------
// PYTHON FINALIZE
//---------------------------------------------
inline void pyf_finalize()
{
	Py_Finalize();
}







