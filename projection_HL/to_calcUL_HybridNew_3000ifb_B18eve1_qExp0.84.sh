
#! /usr/bin/bash

WORK_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/projection_HL"
BASE_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/models/"
cd /afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/projection_HL

python3 $BASE_DIR/run_limitFromDatacard.py --input_datacard /afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/projection_HL/input_combine/scaled3000_B18eve1.txt -w $WORK_DIR -n .3000ifb_B18eve1 -s all -M HybridNew -T 100000 --CL 0.90 -q 0.84

    