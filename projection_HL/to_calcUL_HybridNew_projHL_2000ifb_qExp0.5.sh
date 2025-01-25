
#! /usr/bin/bash

WORK_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/proj_HL"
BASE_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/models/"
cd /afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/proj_HL

python3 $BASE_DIR/run_limitFromDatacard.py --input_datacard /afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/proj_HL/input_combine/scaled2000.txt -w $WORK_DIR -n .projHL_2000ifb -s all -M HybridNew --CL 0.90 -q 0.5

    