#! /usr/bin/bash
DIR='./input_combine'
YEAR='22'
BEST_A='0.####'
BEST_B='0.####'
BEST_C='0.####'
METHOD='HybridNew' #'HybridNew' #'AsymptoticLimits'
CL=0.90

# combine cards
# !!! combine BUG : combine cards not include bkg rate params in kmax value!! (fix by hand)
echo "combineCards.py WTau3Mu_A${YEAR}=${DIR}/datacard_WTau3Mu_A${YEAR}_bdt${BEST_A}.txt WTau3Mu_B${YEAR}=${DIR}/datacard_WTau3Mu_B${YEAR}_bdt${BEST_B}.txt WTau3Mu_C${YEAR}=${DIR}/datacard_WTau3Mu_C${YEAR}_bdt${BEST_C}.txt > ${DIR}/datacard_WTau3Mu_full20${YEAR}.txt"
if [[ $METHOD == 'AsymptoticLimits' ]]; then
    text2workspace.py ${DIR}/datacard_WTau3Mu_full20${YEAR}_$METHOD.txt
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}.root -n .WTau3Mu_full${YEAR} -t -1 --cl $CL
fi
if [[ $METHOD == 'HybridNew' ]]; then
    text2workspace.py ${DIR}/datacard_WTau3Mu_full20${YEAR}.txt --X-assign-flatParam-prior
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.5 --cl $CL
fi

