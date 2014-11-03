#!/bin/sh

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

#set -x #echo on
set -e #exit on failing command

# CHANGE HERE ================================================================
ProjectDir=$PWD
ProjectBuildDir="HARP Build" #sibling to project dir

EclipseProjectName=$ProjectDir         #you may choose your own project name        
EclipseBin="$HOME/bin/eclipse/eclipse" #specify eclipse path!
EclipseVersion="4.3"                   #specify eclipse version!
#=============================================================================

echo "\n"
echo "======================================"
echo "HARP CMake Build System"
echo "======================================"


cd ..
mkdir -p "$ProjectBuildDir";
cd "$ProjectBuildDir"
SleepSeconds=0

# we avoid wildcard rm, since this guy is dangerous
# remove just makes sure that CMake won't cache
#rm -rf ThirdParty
rm -rf CMakeFiles
rm -rf CMakefiles
rm -f Makefile
rm -f CMakeCache.txt
rm -f cmake_install.cmake

if [ ! -f ./.cproject ]; then
    echo "creating and preparing Eclipse project...\n"
    sleep $SleepSeconds
    cmake -G"Eclipse CDT4 - Unix Makefiles" -DPROJECT_NAME=$EclipseProjectName -DCMAKE_ECLIPSE_VERSION=$EclipseVersion -DCMAKE_ECLIPSE_EXECUTABLE=$EclipseBin "$ProjectDir"
    sed -i "s|<name>$EclipseProjectName.*/name>|<name>$EclipseProjectName</name>|g" .project # patching the project name 
else
    echo "existing Eclipse project found, skipping Eclipse project creation...\n"
    sleep $SleepSeconds
    cmake -DPROJECT_NAME=$EclipseProjectName "$ProjectDir"
fi

make -j 4 


