#! /usr/bin/bash
DIR='./input_combine'
YEAR='22'
TAG='LxyS2.1_Optuna_HLT_overlap_2024Jul11_sysT3M100'
BEST_A='0.9940'
BEST_B='0.9970'
BEST_C='0.9930'

METHOD='HybridNew' #'HybridNew' #'AsymptoticLimits'
CL=0.90

# combine cards
# !!! combine BUG : combine cards not include bkg rate params in kmax value!! (fix by hand)
echo "combineCards.py WTau3Mu_A${YEAR}=${DIR}/datacard_WTau3Mu_A${YEAR}_${TAG}_bdt${BEST_A}.txt WTau3Mu_B${YEAR}=${DIR}/datacard_WTau3Mu_B${YEAR}_${TAG}_bdt${BEST_B}.txt WTau3Mu_C${YEAR}=${DIR}/datacard_WTau3Mu_C${YEAR}_${TAG}_bdt${BEST_C}.txt > ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.txt"
if [[ $METHOD == 'AsymptoticLimits' ]]; then
    text2workspace.py ${DIR}/datacard_WTau3Mu_full20${YEAR}.txt
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}.root -n .WTau3Mu_full${YEAR} -t -1 --cl $CL
fi
if [[ $METHOD == 'HybridNew' ]]; then
    echo "-> COMPILING ..."
    text2workspace.py ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.txt --X-assign-flatParam-prior
    # central value
    echo -e "\n-> expUL (90% CL) - central value"
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.50 --cl $CL
    # +/- 1sigma
    echo -e "\n-> expUL (90% CL) - +/- 1sigma"
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.16 --cl $CL
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.84 --cl $CL
    # +/- 2sigma
    echo -e "\n-> expUL (90% CL) - +/- 2sigma"
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.025 --cl $CL
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_full20${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.975 --cl $CL

    # merge results
    hadd higgsCombine.WTau3Mu_full${YEAR}_${TAG}.HybridNew.mH120.root higgsCombine.WTau3Mu_full${YEAR}.HybridNew.mH120.quant*.root 
fi

