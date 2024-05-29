# 2022 A
echo 'Fit catgeory A'
bdt_A=0.999
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p011_2024May10/ --save_ws --double_gaussian --category A -y 22 --bdt_cut ${bdt_A} --combine_dir input_combine/ --tag W3Mf0p011
text2workspace.py input_combine/datacard_WTau3Mu_A22_bdt999_A22_W3Mf0p011.txt
echo '\n\n\n'

#2022 B
echo 'Fit catgeory B'
bdt_B=0.998
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p011_2024May10/ --save_ws --double_gaussian --category B -y 22 --bdt_cut ${bdt_B} --combine_dir input_combine/ --tag W3Mf0p011
text2workspace.py input_combine/datacard_WTau3Mu_B22_bdt998_B22_W3Mf0p011.txt
echo '\n\n\n'
# 2022 C
echo 'Fit catgeory C'
bdt_C=0.997
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p011_2024May10/ --save_ws --double_gaussian --category C -y 22 --bdt_cut ${bdt_C} --combine_dir input_combine/ --tag W3Mf0p011
text2workspace.py input_combine/datacard_WTau3Mu_C22_bdt997_C22_W3Mf0p011.txt
echo '\n\n\n'

combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_A22_bdt999_A22_W3Mf0p011.root -n .WTau3Mu_A22_bdt999 -t -1 --cl 0.90
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_B22_bdt998_B22_W3Mf0p011.root -n .WTau3Mu_B22_bdt9985 -t -1 --cl 0.90
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_C22_bdt997_C22_W3Mf0p011.root -n .WTau3Mu_C22_bdt997 -t -1 --cl 0.90

combineCards.py WTau3Mu_A22=input_combine/datacard_WTau3Mu_A22_bdt999_A22_W3Mf0p011.txt WTau3Mu_B22=input_combine/datacard_WTau3Mu_B22_bdt998_B22_W3Mf0p011.txt WTau3Mu_C22=input_combine/datacard_WTau3Mu_C22_bdt997_C22_W3Mf0p011.txt > input_combine/datacard_WTau3Mu_full2022.txt 
text2workspace.py input_combine/datacard_WTau3Mu_full2022.txt
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_full2022.root -n .WTau3Mu_full22 -t -1 --cl 0.90
