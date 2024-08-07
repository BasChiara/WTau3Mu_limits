# /usr/bin/bash!
cd $COMBINEv10/WTau3Mu_limits/

CATEGORY="ABC"
INPUT_FOLDER="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data"
WORKDIR="$COMBINEv10/WTau3Mu_limits/bdt_cut_optimization"
PLOT_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign"

CUT=3.0
YYYYMonDD="2024Jul26"

echo -e ".... submitting jobs for LxyS > ${CUT} \n"
TAG="kFold_Optuna_HLT_overlap_LxyS${CUT}_${YYYYMonDD}"
OUT_TAG="LxyS${CUT}_Optuna_HLT_overlap_$YYYYMonDD"
python3 scripts/submitBDTopt_onCondor.py -s ${INPUT_FOLDER}/XGBout_signal_${TAG}.root -d ${INPUT_FOLDER}/XGBout_data_${TAG}.root --workdir ${WORKDIR}/binBDT_${OUT_TAG} --tag $OUT_TAG --plot_outdir ${PLOT_DIR}/Training_${TAG}/bdt_scan/ --category $CATEGORY --runtime 12
 
