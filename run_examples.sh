#!/bin/bash

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

source run_settings.sh

echo "\n"
echo "======================================"
echo "HARP $0"
echo "======================================"
echo "See ./bin for results"
echo "HARP_EncArgs: " $HARP_EncArgs
echo "\n"

mkdir -p tmp
cd tmp

# SPECIFIC CODE ===================================

cfg="encoder_lowdelay_P_main"
runEncoder $cfg $cfg
runDecoder $cfg

cfg="encoder_lowdelay_main"
runEncoder $cfg $cfg
runDecoder $cfg

cfg="encoder_randomaccess_main"
runEncoder $cfg $cfg
runDecoder $cfg

# END: SPECIFIC CODE ===============================

echo "\n"
echo "======================================"
echo "Done. See bin directory for results."
echo "======================================"
cd ..
