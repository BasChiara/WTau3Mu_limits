## HLT_DoubleMu 
python3 Tau3Mu_fitSB.py --tag HLT_DoubleMu --save_ws --category A -y 22 --bdt_cut 0.9960

combine -M AsymptoticLimits input_combine/datacard_WTau3Mu_A22_bdt996_A22_HLT_DoubleMu.root -n .WTau3Mu_A22_HLT_DoubleMu -t -1 --cl 0.90
