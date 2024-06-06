#! /usr/bin/bash
#cd ${COMBINE}/WTau3Mu_limits/bdt_cut_optimization/
BASE_DIR='/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/'
COMBINE_DIR="$BASE_DIR/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27/input_combine"
EOS_DIR='/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_HLT_overlap_LxyS1.5_2024May27/bdt_scan/'
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
    #python3 $BASE_DIR/models/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws -s $SIGNAL -d $DATA
    # with AsymptoticLimits
    python3 $BASE_DIR/bdt_cut_optimization/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR  --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY$YEAR -s plot
    # with HybridNew
    echo 'TIME TO CALCULATE LIMITS'
    python3 $BASE_DIR/bdt_cut_optimization/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_$CATEGORY${YEAR}_$TAG.root -d WTau3Mu_$CATEGORY$YEAR -M HybridNew -s plot
done
