# /usr/bin/bash!
cd $COMBINEv10/WTau3Mu_limits/
CATEGORY="ABC"
INPUT_FOLDER="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data"
WORKDIR="$COMBINEv10/WTau3Mu_limits/bdt_cut_optimization"
PLOT_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign"

CUT_LIST=(1.4 1.5 1.7 1.9 2.0)
for CUT in ${CUT_LIST[@]}; do
    echo -e "\n .... submitting jobs for LxyS > ${CUT} \n"
    TAG="kFold_HLT_overlap_LxyS${CUT}_2024May27"
    python3 scripts/submitBDTopt_onCondor.py -s ${INPUT_FOLDER}/XGBout_signal_${TAG}.root -d ${INPUT_FOLDER}/XGBout_data_${TAG}.root --workdir ${WORKDIR}/binBDT_LxyS${CUT}_HLT_overlap_2024May27 --tag HLT_overlap_LxyS${CUT}_2024May27 --plot_outdir ${PLOT_DIR}/Training_${TAG}/bdt_scan/ --category $CATEGORY
done
