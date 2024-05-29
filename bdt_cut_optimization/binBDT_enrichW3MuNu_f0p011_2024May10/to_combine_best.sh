#! /usr/bin/bash
DIR='.'
BEST_A='0.9975'
BEST_B='0.9990'
BEST_C='0.9940'

echo '[+] combine A B C categories'

combineCards.py WTau3Mu_A22=${DIR}/datacard_WTau3Mu_A22_bdt${BEST_A}.txt WTau3Mu_B22=${DIR}/datacard_WTau3Mu_B22_bdt${BEST_B}.txt WTau3Mu_C22=${DIR}/datacard_WTau3Mu_C22_bdt${BEST_C}.txt > ${DIR}/datacard_WTau3Mu_full2022.txt 
text2workspace.py ${DIR}/datacard_WTau3Mu_full2022.txt
combine -M AsymptoticLimits ${DIR}/datacard_WTau3Mu_full2022.root -n .WTau3Mu_full22 -t -1 --cl 0.90

