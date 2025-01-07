#! /usr/bin/bash
DIR='./input_combine'
YEAR='23'
TAG='apply_LxyS2.0_pTVreweight_expo'
BEST_A='0.9870'
BEST_B='0.9960'
BEST_C='0.9920'

METHOD='AsymptoticLimits' #'HybridNew' #'AsymptoticLimits'
CL=0.90

# combine cards
# !!! combine BUG : combine cards not include bkg rate params in kmax value!! (fix by hand)
echo -e "-> command to combine cards\n"
echo "combineCards.py VTau3Mu_A${YEAR}=${DIR}/datacard_VTau3Mu_A${YEAR}_${TAG}_bdt${BEST_A}.txt VTau3Mu_B${YEAR}=${DIR}/datacard_VTau3Mu_B${YEAR}_${TAG}_bdt${BEST_B}.txt VTau3Mu_C${YEAR}=${DIR}/datacard_VTau3Mu_C${YEAR}_${TAG}_bdt${BEST_C}.txt > ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.txt"
if [[ $METHOD == 'AsymptoticLimits' ]]; then
    text2workspace.py ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.txt
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} -t -1 --cl $CL
fi
if [[ $METHOD == 'HybridNew' ]]; then
    echo "-> COMPILING ..."
    text2workspace.py ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.txt --X-assign-flatParam-prior
    # central value
    echo -e "\n-> expUL (90% CL) - median"
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.50 --cl $CL
    # +/- 1sigma
    echo -e "\n-> expUL (90% CL) - +/- 1sigma"
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.16 --cl $CL
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.84 --cl $CL
    # +/- 2sigma
    echo -e "\n-> expUL (90% CL) - +/- 2sigma"
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.025 --cl $CL
    combine -M $METHOD ${DIR}/datacard_VTau3Mu_comb20${YEAR}_${TAG}.root -n .VTau3Mu_comb${YEAR} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.975 --cl $CL

    # merge results
    hadd higgsCombine.VTau3Mu_comb${YEAR}.HybridNew.mH120.root higgsCombine.VTau3Mu_comb${YEAR}.HybridNew.mH120.quant*.root 
fi

