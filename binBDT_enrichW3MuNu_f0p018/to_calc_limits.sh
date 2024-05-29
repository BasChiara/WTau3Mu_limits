# 2022 A
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p018_2024May09/ --save_ws --double_gaussian --category A -y 22 --bdt_cut 0.999 --combine_dir input_combine/
text2workspace.py input_combine/datacard_WTau3Mu_A22_bdt999_A22_emulateRun2.txt

#2022 B
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p018_2024May09/ --save_ws --double_gaussian --category B -y 22 --bdt_cut 0.9985 --combine_dir input_combine/
text2workspace.py input_combine/datacard_WTau3Mu_B22_bdt998_B22_emulateRun2.txt

# 2022 C
python3 ../Tau3Mu_fitSB.py --plot_outdir /eos/user/c/cbasile/www/Tau3Mu_Run3/limits/binBDT_enrichW3MuNu_f0p018_2024May09/ --save_ws --double_gaussian --category C -y 22 --bdt_cut 0.997 --combine_dir input_combine/
text2workspace.py input_combine/datacard_WTau3Mu_C22_bdt997_C22_emulateRun2.txt

combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_A22_bdt999_A22_emulateRun2.root -n .WTau3Mu_A22_bdt999 -t -1 --cl 0.90
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_B22_bdt998_B22_emulateRun2.root -n .WTau3Mu_B22_bdt9985 -t -1 --cl 0.90
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_C22_bdt997_C22_emulateRun2.root -n .WTau3Mu_C22_bdt997 -t -1 --cl 0.90

combineCards.py WTau3Mu_A22=input_combine/datacard_WTau3Mu_A22_bdt999_A22_emulateRun2.txt WTau3Mu_B22=input_combine/datacard_WTau3Mu_B22_bdt998_B22_emulateRun2.txt WTau3Mu_C22=input_combine/datacard_WTau3Mu_C22_bdt997_C22_emulateRun2.txt > input_combine/datacard_WTau3Mu_full2022.txt 
text2workspace.py input_combine/datacard_WTau3Mu_full2022.txt
combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_full2022.root -n .WTau3Mu_full22 -t -1 --cl 0.90