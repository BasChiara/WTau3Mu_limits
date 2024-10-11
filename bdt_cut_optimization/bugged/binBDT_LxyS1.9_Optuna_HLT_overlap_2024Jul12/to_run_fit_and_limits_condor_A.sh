
#! /usr/bin/bash

WORK_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.9_Optuna_HLT_overlap_2024Jul12"
BASE_DIR="/afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/models/"
cd /afs/cern.ch/user/c/cbasile/Combine_v10/CMSSW_14_1_0_pre4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.9_Optuna_HLT_overlap_2024Jul12

TAG="LxyS1.9_Optuna_HLT_overlap_2024Jul12"

COMBINE_DIR="$WORK_DIR/input_combine"

EOS_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_Optuna_HLT_overlap_LxyS1.9_2024Jul12/bdt_scan/"
YEAR="22"
SIGNAL="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_signal_kFold_Optuna_HLT_overlap_LxyS1.9_2024Jul12.root"
DATA="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_data_kFold_Optuna_HLT_overlap_LxyS1.9_2024Jul12.root"

CATEGORY="A"

echo -e "
"
echo    "|  CATEGORY $CATEGORY  |"
echo -e "
"
echo 'TIME TO FIT'
#python3 $BASE_DIR/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL -d $DATA --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws --bkg_func dynamic --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005
echo 'TIME TO CALCULATE LIMITS'
# with AsymptoticLimits
python3 $BASE_DIR/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12.root -d WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 -n WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005 -s all
# with HybridNew 
python3 $BASE_DIR/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12.root -d WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 -n WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 -M HybridNew --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005 -s all
echo 'TIME TO COMPARE THE METHODS'
# compare the methods
python3 $BASE_DIR/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12_BDTscan.AsymptoticLimits.root --labels AsymptoticLimits --inputs input_combine/Tau3MuCombine.WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12_BDTscan.HybridNew.root --labels HybridNew -o $EOS_DIR -d WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 -n WTau3Mu_A22_LxyS1.9_Optuna_HLT_overlap_2024Jul12 -y 20$YEAR -c $CATEGORY
    