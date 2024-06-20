#! /usr/bin/bash
#cd ${COMBINE}/WTau3Mu_limits/bdt_cut_optimization/
BASE_DIR="/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/"
WORK_DIR="#WORKING_DIR#"
TAG="#TAG#"

COMBINE_DIR="$BASE_DIR/bdt_cut_optimization/$WORK_DIR/input_combine"

EOS_DIR="#EOS_DIR#"
YEAR="#YEAR#"
SIGNAL="#SIGNAL_SAMPLE#"
DATA="#DATA_SAMPLE#"

CATEGORY="#CATEGORY#"

echo -e "\n----------------"
echo    "|  CATEGORY $CATEGORY  |"
echo -e "----------------\n"

FULL_TAG="WTau3Mu_${CATEGORY}${YEAR}_${TAG}"

echo 'TIME TO FIT'
python3 $BASE_DIR/models/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL -d $DATA --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws --bkg_func dynamic
echo 'TIME TO CALCULATE LIMITS'
# with AsymptoticLimits
python3 $BASE_DIR/models/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_$FULL_TAG.root -d $FULL_TAG -n $FULL_TAG -s all 
# with HybridNew
python3 $BASE_DIR/models/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$FULL_TAG.root -d $FULL_TAG -n WTau3Mu_$FULL_TAG -M HybridNew -s all
# compare the methods
python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.${FULL_TAG}_BDTscan.AsymptoticLimits.root --labels AsymptoticLimits --inputs input_combine/Tau3MuCombine.${FULL_TAG}_BDTscan.HybridNew.root --labels HybridNew -o $EOS_DIR -d $FULL_TAG -n $FULL_TAG -y 20$YEAR

# compare with expo-only bkg fit
python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels 'AL-const' --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels 'HN-const' --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels AL-expo --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels HN-expo -o $EOS_DIR -t HNvsAL_expoVSconst -d WTau3Mu_$CATEGORY${YEAR} -n WTau3Mu_$CATEGORY${YEAR} -y 20$YEAR

