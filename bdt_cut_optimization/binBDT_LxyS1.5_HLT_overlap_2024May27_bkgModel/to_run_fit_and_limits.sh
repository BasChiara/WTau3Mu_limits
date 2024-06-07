#! /usr/bin/bash
#cd ${COMBINE}/WTau3Mu_limits/bdt_cut_optimization/
BASE_DIR='/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/'
COMBINE_DIR="$BASE_DIR/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27_bkgModel/input_combine"
EOS_DIR='/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_HLT_overlap_LxyS1.5_2024May27/bdt_scan_bkgModel/'
YEAR=22
TAG='HLT_overlap_LxyS1.5_2024May27'
SIGNAL='/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_signal_kFold_HLT_overlap_LxyS1.5_2024May27.root'
DATA='/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_data_kFold_HLT_overlap_LxyS1.5_2024May27.root'

# 2022
CATEGORY_LIST=("A" "B" "C")
for CATEGORY in ${CATEGORY_LIST[@]}; do
    echo -e "\n----------------"
    echo    "|  CATEGORY $CATEGORY  |"
    echo -e "----------------\n"
    echo 'TIME TO FIT'
    #python3 $BASE_DIR/models/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL -d $DATA --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws --const_lowB
    echo 'TIME TO CALCULATE LIMITS'
    # with AsymptoticLimits
    #python3 $BASE_DIR/bdt_cut_optimization/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY$YEAR -n WTau3Mu_$CATEGORY$YEAR -s all 
    # with HybridNew
    #python3 $BASE_DIR/bdt_cut_optimization/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY$YEAR -n WTau3Mu_$CATEGORY$YEAR -M HybridNew -s all
    # compare the methods
    #python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels AsymptoticLimits --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels HybridNew -o $EOS_DIR -d WTau3Mu_$CATEGORY${YEAR} -n WTau3Mu_$CATEGORY${YEAR} -y 20$YEAR

    # compare with expo-only bkg fit
    python3 $BASE_DIR/models/compareLimitScan.py --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels 'AL-expo/const' --inputs input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels 'HN-expo/const' --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.AsymptoticLimits.root --labels AL-expo --inputs ../binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine/Tau3MuCombine.WTau3Mu_$CATEGORY${YEAR}_BDTscan.HybridNew.root --labels HN-expo -o $EOS_DIR -t HNvsAL_expoVSconst -d WTau3Mu_$CATEGORY${YEAR} -n WTau3Mu_$CATEGORY${YEAR} -y 20$YEAR
done
