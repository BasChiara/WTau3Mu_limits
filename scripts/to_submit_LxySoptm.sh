# /usr/bin/bash!
cd $COMBINEv10/WTau3Mu_limits/
CATEGORY="ABC"
INPUT_FOLDER="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/output/"
WORKDIR="$COMBINEv10/WTau3Mu_limits/bdt_cut_optimization"
PLOT_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/"

YEAR=("22" "23")
CUT_LIST=(2.0)
YYYYMonDD="2024Oct10"
for Y in ${YEAR[@]}; do
    for CUT in ${CUT_LIST[@]}; do
        echo -e "\n .... submitting jobs for LxyS > ${CUT} year ${Y}\n"
        
        TAG="kFold_Optuna_HLT_overlap_apply_LxyS${CUT}_${YYYYMonDD}"
        OUT_TAG="LxyS${CUT}_Optuna_HLT_overlap_apply_$YYYYMonDD"
        
        python3 scripts/submitBDTopt_onCondor.py -s ${INPUT_FOLDER}/XGBout_signal_${TAG}.root -d ${INPUT_FOLDER}/XGBout_data_${TAG}.root --workdir ${WORKDIR}/binBDT_$OUT_TAG --tag $OUT_TAG --plot_outdir ${PLOT_DIR}/Training_${TAG}/bdt_scan/ --category $CATEGORY --year $Y --runtime 12 --BDTmin 0.9850 --BDTmax 0.9990 --BDTstep 0.0010 
    done
done
