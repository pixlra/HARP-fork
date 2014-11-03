# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

# CHANGE HERE ================================================================
option (DEBUG "Compile as Debug" ON)               # ON/OFF
option (COMPILE_ENCODER "Compile Encoder" ON)      # ON/OFF, do you need the decoder?
option (COMPILE_DECODER "Compile Decoder" ON)      # ON/OFF, do you need the decoder?
option (ACTIVATE_NEXT   "Activate Next branch" OFF) # ON/OFF, development branch (leave off)
#=============================================================================

#------------------------------------
# Project setup
#------------------------------------
set(PROJECT_NAME "HARP_PROJECT" CACHE STRING "Overridden by build_outofsource")
project(${PROJECT_NAME})
cmake_minimum_required(VERSION 2.8)
set(RootDir "${CMAKE_CURRENT_SOURCE_DIR}") # change here if CMakeLists location changes
set(HM_Dir  "Src_HM") # change here if CMakeLists location changes

#------------------------------------
# Release or Debug build
#------------------------------------
IF(DEBUG STREQUAL "ON")
    MESSAGE( STATUS "\n================== DEBUG BUILD ==================\n")
    set( CMAKE_BUILD_TYPE "Debug" )
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0")
ELSEIF (DEBUG STREQUAL "OFF")
    MESSAGE( STATUS "\n================ RELEASE BUILD =================\n")
    set( CMAKE_BUILD_TYPE "Release" ) 
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g") 
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3") #fast release build with symbols
ELSE()
    MESSAGE (FATAL_ERROR "Unkown Build Type")
ENDIF()

#------------------------------------
# Definitions
#------------------------------------
IF(ACTIVATE_NEXT STREQUAL "ON")
    MESSAGE( STATUS "WARNING: Next branch active")
    add_definitions( -DACTIVATE_NEXT )
ENDIF()
add_definitions( -DLARGEFILE64_SOURCE )
add_definitions( -DMSYS_UNIX_LARGEFILE )
add_definitions( -D_FILE_OFFSET_BITS=64 )

#------------------------------------
# Extra CXX_FLAGS
#------------------------------------
set(SpecialIncludeDirs "/usr/include") #"/usr/include/c++/4.8" 
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -I/usr/include")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DMSYS_LINUX ") # -march=native #-fpermissive # C++0x def: -std=c++0x #-std=c++11

#------------------------------------
# Output & module paths
#------------------------------------
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}" "${RootDir}/Various/ThirdParty/FindNumPy" ) #location of Find*.cmake scripts
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${RootDir}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${RootDir}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${RootDir}/bin)


#------------------------------------
# Importing Python + Numpy
#------------------------------------
MESSAGE( STATUS "\n__________PYTHON + NUMPY_____________")
#add_definitions( -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION ) # cannot force new numpy API (FIXME)
find_package ( PythonLibs REQUIRED )
MESSAGE( STATUS "PYTHON_LIBRARIES=${PYTHON_LIBRARIES}")
MESSAGE( STATUS "PYTHON_INCLUDE_PATH=${PYTHON_INCLUDE_PATH}")
find_package ( NumPy REQUIRED  )
MESSAGE( STATUS "NUMPY_INCLUDE_DIRS=${NUMPY_INCLUDE_DIRS}")

#------------------------------------
# Importing OpenCV
#------------------------------------
# Uncomment to include custom OpenCV
MESSAGE( STATUS "\n_______________OPENCV_______________")
set(MY_OPENCV_SEARCH_DIR "$ENV{HOME}/lib/OPENCV_2.4.9/share/OpenCV")  
set(OpenCV_DIR ${MY_OPENCV_SEARCH_DIR} CACHE LOCATION "OpenCV search dir")
find_package(OpenCV REQUIRED)

#MESSAGE( STATUS "IncludeDirs=${IncludeDirs}")
MESSAGE( STATUS "OpenCV_FOUND=${OpenCV_FOUND}")
MESSAGE( STATUS "OpenCV_LIB_DIR=${OpenCV_LIB_DIR}")
MESSAGE( STATUS "OpenCV_INCLUDE_DIRS=${OpenCV_INCLUDE_DIRS}")
MESSAGE( STATUS "OpenCV_LIBS=${OpenCV_LIBS}")

#------------------------------------
# Importing Qt
#------------------------------------
MESSAGE( STATUS "\n_______________QT_______________")
find_package ( Qt4 COMPONENTS QtCore QTGui QtXml REQUIRED )
include ( ${QT_USE_FILE} )

#MESSAGE( STATUS "application_SRCS=${application_SRCS}")
#MESSAGE( STATUS "UIS=${UIS}")
#MESSAGE( STATUS "RSCS=${RSCS}")
#MESSAGE( STATUS "TRS=${TRS}")
#MESSAGE( STATUS "MOCS=${MOCS}")
MESSAGE( STATUS "QT_QTCORE_INCLUDE_DIR=${QT_QTCORE_INCLUDE_DIR}")
MESSAGE( STATUS "QT_QTGUI_INCLUDE_DIR=${QT_QTGUI_INCLUDE_DIR}")
MESSAGE( STATUS "QT_QTCORE_LIBRARY=${QT_QTCORE_LIBRARY}")
MESSAGE( STATUS "QT_QTGUI_LIBRARY=${QT_QTGUI_LIBRARY}")

#------------------------------------
# Special: singe file compile flags
#------------------------------------
#LIST(REMOVE_ITEM srcs ${RootDir}/HM/source/Lib/TLibCommon/TComPrediction.cpp)
#MESSAGE( STATUS "SRCS=${srcs}")
# THEN, AT THE TARGETS:
#SET_SOURCE_FILES_PROPERTIES( ${RootDir}/HM/source/Lib/TLibCommon/TComPrediction.cpp PROPERTIES COMPILE_FLAGS "-g -O0" )
#SET_SOURCE_FILES_PROPERTIES( ${RootDir}/HM/source/Lib/TLibEncoder/TEncCu.cpp PROPERTIES COMPILE_FLAGS "-g -O0" )
#SET_SOURCE_FILES_PROPERTIES( ${RootDir}/HM/source/Lib/TLibEncoder/TEncSlice.cpp PROPERTIES COMPILE_FLAGS "-g -O0" )

#------------------------------------
# Importing Boost
#------------------------------------
#set (Boost_NO_SYSTEM_PATHS true)
#set (BOOST_ROOT "$ENV{HOME}/inst_boost_1.49")
#find_package(Boost COMPONENTS serialization thread date_time program_options filesystem system REQUIRED)

#------------------------------------
# libptools (DISABLED)
#------------------------------------
#add_library( ptools SHARED IMPORTED )
#set_target_properties( ptools PROPERTIES IMPORTED_LOCATION "${RootDir}/LMS/PicklingTools151Release/libptools.so")
#set(PTOOLS_LIBDIR "${RootDir}/LMS/PicklingTools151Release") 
#add_subdirectory(ThirdParty) #port of ptools to CMake
#set(PTOOLS_INCLUDE_DIRS "${RootDir}/ThirdParty/libptools" "${RootDir}/ThirdParty/libptools/opencontainers_1_7_7/include") 
#set(PTOOLS_LIBS "ptools")
#set(CXX_FLAGS_PTOOLS "-fpic -g -fno-strict-aliasing -DLINUX_ -DOC_NEW_STYLE_INCLUDES -Wno-deprecated -pthread -D_REENTRANT")
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_FLAGS_PTOOLS}")

# =============================================================
# SETTING UP INCLUDE DIRS
# =============================================================
# make sure /usr/include is stated, otherwise indexer for system-installed opencv won't work 
set(ExternalIncludeDirs ${OpenCV_INCLUDE_DIRS} ${QT_INCLUDES} ${Boost_INCLUDE_DIR} ${PYTHON_INCLUDE_PATH} ${NUMPY_INCLUDE_DIRS} ${PTOOLS_INCLUDE_DIRS})
set(IncludeDirs ${RootDir} "${RootDir}/Src_HARP" "${RootDir}/Next" "${RootDir}/Src_HM/source/Lib" "${RootDir}/Src_HM/source" "${RootDir}/Various/ThirdParty/opencv")
include_directories(${IncludeDirs} ${SpecialIncludeDirs} ${ExternalIncludeDirs})

# =============================================================
# SETTING UP COMMON SOURCES
# =============================================================

#------------------------------------
# Sources OWN
#------------------------------------
IF(ACTIVATE_NEXT STREQUAL "ON")
    #set(srcsNext "${RootDir}/Next/Proxy.cpp"  ) # place NEXT sources here   
ENDIF()

#QT4_WRAP_CPP(out_MOCS ${RootDir}/LMS/GUI/CHarpGUI.h)
#set (srcsGUI ${RootDir}/LMS/GUI/CHarpGUI.cpp ${out_MOCS})
file(GLOB srcsOWN       "${RootDir}/Src_HARP/*.cpp" )             # Sources OWN
file(GLOB srcs3rdParty  "${RootDir}/Various/ThirdParty/opencv/*.cpp")   # Sources ThirdParty

#------------------------------------
# Sources HM 
#------------------------------------
file(GLOB srcsVideoIO   "${HM_Dir}/source/Lib/TLibVideoIO/*.cpp")   # Sources VideoIO
file(GLOB srcsMD5       "${HM_Dir}/source/Lib/libmd5/*.c")              # Sources md5
file(GLOB srcsLibCommon "${HM_Dir}/source/Lib/TLibCommon/*.cpp")  # Sources LibCommon
set(srcsLibCommon ${srcsOWN} ${srcs3rdParty} ${srcsVideoIO} ${srcsMD5} ${srcsLibCommon}) 

file(GLOB srcsAppCommon  "${HM_Dir}/source/Lib/TAppCommon/*.cpp")  # Sources AppCommon
file(GLOB srcsLibEncoder "${HM_Dir}/source/Lib/TLibEncoder/*.cpp") # Sources LibEncoder
file(GLOB srcsAppEncoder "${HM_Dir}/source/App/TAppEncoder/*.cpp") # Sources TAppEncoder
file(GLOB srcsLibDecoder "${HM_Dir}/source/Lib/TLibDecoder/*.cpp") # Sources TLibDecoder
file(GLOB srcsAppDecoder "${HM_Dir}/source/App/TAppDecoder/*.cpp") # Sources TAppDecoder

MESSAGE( STATUS "\n_______________ ENVIRONMENT _______________")
MESSAGE( STATUS "IncludeDirs=${IncludeDirs}")
MESSAGE( STATUS "ExternalIncludeDirs=${ExternalIncludeDirs}")
MESSAGE( STATUS "Home directory=$ENV{HOME}")
MESSAGE( STATUS "OpenCV_LIB_DIR=${OpenCV_LIB_DIR}")

# =============================================================
# TARGET: ENCODER
# =============================================================
IF(COMPILE_ENCODER STREQUAL "ON")    
    MESSAGE( STATUS "\n_____________ ENCODER ____________")

    set(BinaryName "TAppEncoder") 
    add_executable(${BinaryName} ${srcsLibCommon} ${srcsLibEncoder} ${srcsAppCommon} ${srcsAppEncoder} )
    link_directories("${RootDir}/build" ${Boost_LIBRARY_DIR})             
    target_link_libraries(${BinaryName} ${QT_LIBRARIES} ${OpenCV_LIBS} ${Boost_LIBRARIES} ${PYTHON_LIBRARIES} ${PTOOLS_LIBS})
    
    MESSAGE( STATUS "srcsOWN=${srcsOWN}")
    MESSAGE( STATUS "srcs3rdParty=${srcs3rdParty}")
    MESSAGE( STATUS "srcsLibCommon=${srcsLibCommon}")
    MESSAGE( STATUS "srcsLibEncoder=${srcsLibEncoder}")
    MESSAGE( STATUS "srcsAppCommon=${srcsAppCommon}")
    MESSAGE( STATUS "srcsAppEncoder=${srcsAppEncoder}")
    
ENDIF()

# =============================================================
# TARGET: DECODER
# =============================================================
IF(COMPILE_DECODER STREQUAL "ON")
    MESSAGE( STATUS "\n_____________ DECODER ____________")

    set(BinaryName "TAppDecoder") 
    add_executable(${BinaryName} ${srcsLibCommon} ${srcsLibDecoder} ${srcsAppCommon} ${srcsAppDecoder} )
    link_directories("${RootDir}/build" ${Boost_LIBRARY_DIR}) 
    target_link_libraries(${BinaryName} ${QT_LIBRARIES} ${OpenCV_LIBS} ${Boost_LIBRARIES} ${PYTHON_LIBRARIES} ${PTOOLS_LIBS})
    
    MESSAGE( STATUS "srcsOWN=${srcsOWN}")
    MESSAGE( STATUS "srcs3rdParty=${srcs3rdParty}")
    MESSAGE( STATUS "srcsLibCommon=${srcsLibCommon}")
    MESSAGE( STATUS "srcsLibDecoder=${srcsLibDecoder}")
    MESSAGE( STATUS "srcsAppCommon=${srcsAppCommon}")
    MESSAGE( STATUS "srcsAppDecoder=${srcsAppDecoder}")
    
ENDIF()



#FOREACH(entry ${srcs})
#MESSAGE(STATUS "  ${entry}")
#ENDFOREACH(entry)

