# /usr/bin/bash!
cd $CMSSW_BASE/src/WTau3Mu_limits/

CATEGORY="ABC"
INPUT_FOLDER="/eos/user/c/cbasile/Tau3MuRun3/data/mva_data/output/"
WORKDIR="$CMSSW_BASE/src/WTau3Mu_limits/bdt_cut_optimization"
PLOT_DIR="/eos/user/c/cbasile/www/Tau3Mu_Run3/BPH-24-010_review/LxyS-efficiency/BDTscan/"

YEAR=23 #23
YYYYMonDD="2025Jul25"

echo -e ".... submitting jobs for 20${YEAR} \n"
TAG="kFold_LxyS-sameffyear_${YYYYMonDD}"
OUT_TAG=$TAG
python3 scripts/submitBDTopt_onCondor.py --workdir ${WORKDIR}/binBDT_${OUT_TAG} --tag $OUT_TAG --plot_outdir ${PLOT_DIR} --category $CATEGORY --year $YEAR --BDTmin 0.9850 --BDTmax 0.9990 --BDTstep 0.0010 --runtime 12
