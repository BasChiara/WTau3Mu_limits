#! /usr/bin/bash
cd ${COMBINE}/WTau3Mu_limits/bdt_cut_optimization/
COMBINE_DIR='binBDT_LxyS1.5_HLT_overlap_2024Apr29/'
YEAR=22

# 2022
# CATEGORY A
CATEGORY='A'
echo '\n------------------------'
echo '|  CATEGORY ${CATEGORY}|'
echo '------------------------\n'
python3 Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/Training_kFold_HLT_overlap_LxyS150_2024Apr29/bdt_scan/ --combine_dir ${COMBINE_DIR} --category A -y ${YEAR} --tag HLT_overlap_LxyS150_2024Apr29 --double_gaussian --optim_bdt --save_ws
python3 run_optimization.py -i ${COMBINE_DIR} -s all -d WTau3Mu_${CATEGORY}${YEAR}

# CATEGORY B
CATEGORY='B'
echo '\n------------------------'
echo '|  CATEGORY ${CATEGORY}|'
echo '------------------------\n'
python3 Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/Training_kFold_HLT_overlap_LxyS150_2024Apr29/bdt_scan/ --combine_dir ${COMBINE_DIR} --category B -y ${YEAR} --tag HLT_overlap_LxyS150_2024Apr29 --double_gaussian --optim_bdt --save_ws
echo run_optimization.py -i ${COMBINE_DIR} -s all -d WTau3Mu_${CATEGORY}${YEAR} 
python3 run_optimization.py -i ${COMBINE_DIR} -s all -d WTau3Mu_${CATEGORY}${YEAR}

# CATEGORY C
CATEGORY='C'
echo '\n------------------------'
echo '|  CATEGORY ${CATEGORY}|'
echo '------------------------\n'
python3 Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/Training_kFold_HLT_overlap_LxyS150_2024Apr29/bdt_scan/ --combine_dir ${COMBINE_DIR} --category ${CATEGORY} -y ${YEAR} --tag HLT_overlap_LxyS150_2024Apr29 --double_gaussian --optim_bdt --save_ws
echo run_optimization.py -i ${COMBINE_DIR} -s all -d WTau3Mu_${CATEGORY}${YEAR} 
python3 run_optimization.py -i ${COMBINE_DIR} -s all -d WTau3Mu_${CATEGORY}${YEAR} --Bmax 0.9985
