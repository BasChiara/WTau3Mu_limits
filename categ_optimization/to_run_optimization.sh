#! /usr/bin/bash

SIGNAL_FILE='/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_signal_kFold_HLT_overlap_LxyS1.5_2024May27.root'
DATA_FILE='/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/XGBout_data_kFold_HLT_overlap_LxyS1.5_2024May27.root'
YEAR='22'
BDT_CUT=0.995

python3 ../models/categories_optimization.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/categorization/optimize_eta/sig_bkg_fit/ --combine_dir input_combine -s $SIGNAL_FILE -d $DATA_FILE --save_ws -y $YEAR --bdt_cut $BDT_CUT
python3 ../models/runCatOptimCombine.py -i input_combine -d WTau3Mu -n WTau3Mu -M AsymptoticLimits --bdt_cut $BDT_CUT -y $YEAR
