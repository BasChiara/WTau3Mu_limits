#!/bin/bash

# 2022
cd /eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/bdt_cut_optimization/
COMBINE_DIR='./binBDT_enrichW3MuNu_f0p011_2024May10/'
EOS_DIR='/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/Training_kFold_fW3m0p011_enrichW3MuNu_2024May10/bdt_scan'
TAG='enrichW3MuNu_f0p011_2024May10'
YEAR=22
SIGNAL_FILE='/eos/user/c/cbasile/Tau3MuRun3/data/mva_W3MuNuEnrich_data/XGBout_signal_kFold_fW3m0p011_enrichW3MuNu_2024May10.root'
DATA_FILE='/eos/user/c/cbasile/Tau3MuRun3/data/mva_W3MuNuEnrich_data/XGBout_data_kFold_fW3m0p011_enrichW3MuNu_2024May10.root'
#CATEGORY_LIST=("A" "B" "C")
CATEGORY_LIST=("C")

for CATEGORY in ${CATEGORY_LIST[@]}; do
    echo -e "\n----------------"
    echo "|  CATEGORY $CATEGORY  |"
    echo -e "----------------\n"

    echo 'IT IS TIME TO FIT'
    #python3 Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL_FILE -d $DATA_FILE --category $CATEGORY -y $YEAR --tag $TAG --double_gaussian --optim_bdt --save_ws
    echo 'IT IS TIME TO OPTIMIZE CUT'
    python3 run_optimization.py -i $COMBINE_DIR -s merge -d WTau3Mu_$CATEGORY$YEAR -n $TAG

done