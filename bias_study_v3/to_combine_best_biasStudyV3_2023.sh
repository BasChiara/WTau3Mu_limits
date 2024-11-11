#! /usr/bin/bash
DIR='./input_combine'
YEAR='23'
TAG='kFold_Optuna_HLT_overlap_LxyS2.0_2024Jul16_const'
BEST_A='0.9870'
BEST_B='0.9960'
BEST_C='0.9920'

METHOD='HybridNew' #'HybridNew' #'AsymptoticLimits'
CL=0.90

# combine cards
# !!! combine BUG : combine cards not include bkg rate params in kmax value!! (fix by hand)
echo -e "-> command to combine cards\n"
echo "combineCards.py WTau3Mu_A${YEAR}=${DIR}/datacard_WTau3Mu_A${YEAR}_${TAG}_bdt${BEST_A}.txt WTau3Mu_B${YEAR}=${DIR}/datacard_WTau3Mu_B${YEAR}_${TAG}_bdt${BEST_B}.txt WTau3Mu_C${YEAR}=${DIR}/datacard_WTau3Mu_C${YEAR}_${TAG}_bdt${BEST_C}.txt > ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.txt"
if [[ $METHOD == 'AsymptoticLimits' ]]; then
    text2workspace.py ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.txt
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} -t -1 --cl $CL
fi
if [[ $METHOD == 'HybridNew' ]]; then
    echo "-> COMPILING ..."
    text2workspace.py ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.txt --X-assign-flatParam-prior
    # central value
    echo -e "\n-> expUL (90% CL) - median"
    combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.50 --cl $CL
    # +/- 1sigma
    echo -e "\n-> expUL (90% CL) - +/- 1sigma"
    #combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.16 --cl $CL
    #combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.84 --cl $CL
    # +/- 2sigma
    echo -e "\n-> expUL (90% CL) - +/- 2sigma"
    #combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.025 --cl $CL
    #combine -M $METHOD ${DIR}/datacard_WTau3Mu_comb${YEAR}_${TAG}.root -n .WTau3Mu_full${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.975 --cl $CL

    # merge results
    #hadd higgsCombine.WTau3Mu_comb${YEAR}.HybridNew.mH120.root higgsCombine.WTau3Mu_full${YEAR}.HybridNew.mH120.quant*.root 
fi

