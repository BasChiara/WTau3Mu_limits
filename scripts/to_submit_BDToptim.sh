# /usr/bin/bash!
cd $COMBINEv10/WTau3Mu_limits/

CATEGORY="ABC"
INPUT_FOLDER="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/output/"
WORKDIR="$COMBINEv10/WTau3Mu_limits/bdt_cut_optimization"
PLOT_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign"

CUT=0.0
YYYYMonDD="2024Aug27"

echo -e ".... submitting jobs for LxyS > ${CUT} \n"
TAG="kFold_HLT_overlap_limOT_${YYYYMonDD}"
OUT_TAG="LxyS${CUT}_HLT_overlap_reprocess_$YYYYMonDD"
python3 scripts/submitBDTopt_onCondor.py -s ${INPUT_FOLDER}/XGBout_signal_${TAG}.root -d ${INPUT_FOLDER}/XGBout_data_${TAG}.root --workdir ${WORKDIR}/binBDT_${OUT_TAG} --tag $OUT_TAG --plot_outdir ${PLOT_DIR}/Training_${TAG}/bdt_scan/ --category $CATEGORY --runtime 12  --BDTmin 0.9700 --BDTmax 0.9980 --BDTstep 0.0020
 
