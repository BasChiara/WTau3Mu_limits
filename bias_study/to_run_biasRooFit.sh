#! /bin/bash

CATEGORY_LIST=("A" "B" "C")
FIT_FUNC_LIST=("const" "expo")
R_GEN_LIST=(0.0 0.5 1.0 10.0)
BDT_CUT=0.9940

for CATEGORY in ${CATEGORY_LIST[@]}; do
    if [ $CATEGORY == "B" ]; then
       BDT_CUT=0.9970 
    fi
    if [ $CATEGORY == "C" ]; then
       BDT_CUT=0.9930 
    fi
    for FIT_FUNC in ${FIT_FUNC_LIST[@]}; do
        for R_GEN in ${R_GEN_LIST[@]}; do
            echo -e "\n----------------"
            echo    "|  CATEGORY $CATEGORY  |"
            echo    "|  FIT_FUNC $FIT_FUNC  |"
            echo    "|  R_GEN $R_GEN  |"
            echo -e "----------------\n"

            #python3 RunBiasRooFit.py --input_datacard input_combine/datacard_WTau3Mu_${CATEGORY}22_LxyS2.1_2024Jul11_${FIT_FUNC}_bdt${BDT_CUT}.root --gen_func expo --fit_func $FIT_FUNC --nToys 50000 -c $CATEGORY -y 22 --r_gen $R_GEN --tag WTau3Mu_${CATEGORY}22_LxyS2.1_2024Jul11_bdt${BDT_CUT} --nFit 30000

            python3 plot_bias_pull.py --input_root fit_results/fitResults_fit${FIT_FUNC}.gen50Kexpo_WTau3Mu_${CATEGORY}22_LxyS2.1_2024Jul11_bdt${BDT_CUT}_r${R_GEN}.root --method roofit --gen_func expo --fit_func $FIT_FUNC --plot_outdir ./fit_plots/ --tag ${CATEGORY}22 --r_gen $R_GEN
        done
    done
done