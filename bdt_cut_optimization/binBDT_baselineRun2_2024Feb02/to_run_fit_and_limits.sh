#! /usr/bin/bash
#cd ${COMBINE}/WTau3Mu_limits/bdt_cut_optimization/
BASE_DIR="/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/"
WORK_DIR="binBDT_baselineRun2_2024Feb02"
TAG="2024Feb02_HLT_overlap"
COMBINE_DIR="$BASE_DIR/bdt_cut_optimization/$WORK_DIR/input_combine/"
EOS_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/Training_kFold_2024Feb02/bdt_scan/"
YEAR=22
SIGNAL="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_WTau3Mu_MC_BDT_2024Feb02_HLT_overlap.root"
DATA="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_WTau3Mu_DATA_BDT_2024Feb02_HLT_overlap.root"

# 2022
CATEGORY_LIST=("A" "B" "C")
for CATEGORY in ${CATEGORY_LIST[@]}; do
    echo -e "\n----------------"
    echo    "|  CATEGORY $CATEGORY  |"
    echo -e "----------------\n"
    echo 'TIME TO FIT'
    python3 $BASE_DIR/models/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL -d $DATA --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws --bkg_func dynamic
    echo 'TIME TO CALCULATE LIMITS'
    # with AsymptoticLimits
    python3 $BASE_DIR/models/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY${YEAR}_$TAG -n WTau3Mu_$CATEGORY$YEAR --BDTstep 0.001 -s plot 
    # with HybridNew
    python3 $BASE_DIR/models/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY${YEAR}_$TAG -n WTau3Mu_$CATEGORY$YEAR --BDTstep 0.001  -M HybridNew -s plot
    # compare methods
    python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_${TAG}_BDTscan.AsymptoticLimits.root --labels AsymptoticLimits --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_${TAG}_BDTscan.HybridNew.root --labels HybridNew -o $EOS_DIR -d WTau3Mu_$CATEGORY${YEAR}_$TAG -n WTau3Mu_$CATEGORY${YEAR} -y 20$YEAR

    # compare with expo-only bkg fit
    #python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels 'AL-const' --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels 'HN-const' --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels AL-expo --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels HN-expo -o $EOS_DIR -t HNvsAL_expoVSconst -d WTau3Mu_$CATEGORY${YEAR} -n WTau3Mu_$CATEGORY${YEAR} -y 20$YEAR
done
