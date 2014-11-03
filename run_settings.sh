#!/bin/sh

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)


#set -x #echo on
set -e #exit on failing command

#------------ Change or override here: ----------------------------
NumFr=3
Sequence="../Various/Resources/Special/LMS_Logo_640x360.yuv --SourceWidth=640 --SourceHeight=360"
#------------------------------------------------------------------

# File IO
BitstreamFN="str.bin"
ReconFN="rec.yuv" 
ReconFN_DEC="rec_DEC.yuv" 

# Encoder
EncBin="../bin/TAppEncoder"
EncArgs="--QP=10 --FrameRate=30 --InputBitDepth=8 --FrameSkip=0"
HARP_EncArgs=" --HARP_ObsPOCs=0,1,2,3 --HARP_ObsCTUs=14 --HARP_PUs --HARP_TUs --HARP_RefIndices --HARP_UnitCloseup --HARP_RDO"

# Decoder
DecBin="../bin/TAppDecoder"
DecArgs=" -b $BitstreamFN -o $ReconFN_DEC"

# ValgrindPrefix
ValgrindPrefix=""

runEncoder(){
	local cfg="$1"
    local TmpDir="$2"
    mkdir -p $TmpDir
    echo "\n"
    echo "--------------------------------------"
    echo "Running Encoder ($cfg)"
    echo "--------------------------------------"

    $ValgrindPrefix $EncBin -c ../Src_HM/cfg/$cfg.cfg -i $Sequence $EncArgs -f $NumFr -b $TmpDir/$BitstreamFN -o $TmpDir/$ReconFN $HARP_EncArgs --HARP_TmpDir=$TmpDir
    #$DecBin -b $BitstreamFN -o $ReconFN_DEC
}

runDecoder(){
    local TmpDir="$1"
    mkdir -p $TmpDir
    echo "\n"
    echo "--------------------------------------"
    echo "Running Decoder"
    echo "--------------------------------------"

    $DecBin -b $TmpDir/$BitstreamFN -o $TmpDir/$ReconFN_DEC --HARP_TmpDir=$TmpDir
}


