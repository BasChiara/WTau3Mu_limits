import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.EnableImplicitMT()
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep

LxyS_cuts = np.asarray([1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1] )

input_root = [
    'None', # 1.3 
    'binBDT_LxyS1.4_Optuna_HLT_overlap_2024Jul12/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 1.4
    'binBDT_LxyS1.5_Optuna_HLT_overlap_2024Jul26/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 1.5
    'None', # 1.6
    'binBDT_LxyS1.7_Optuna_HLT_overlap_2024Jul12/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 1.7
    'None', # 1.8
    'binBDT_LxyS1.9_Optuna_HLT_overlap_2024Jul12/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 1.9
    'binBDT_LxyS2.0_Optuna_HLT_overlap_2024Jul16/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 2.0
    'binBDT_LxyS2.1_Optuna_HLT_overlap_2024Jul11/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 2.1
    'None', # 2.2
    'None', # 2.3
    'None', # 2.4
    'None', # 2.5
    'None', # 2.6
    'None', # 2.7
    'None', # 2.8
    'None', # 2.9
    'binBDT_LxyS3.0_Optuna_HLT_overlap_2024Jul26/higgsCombine.WTau3Mu_full22.HybridNew.mH120.root', # 3.0 
    'None', # 3.1
]

LxyS_cuts_file_dict = dict(zip(LxyS_cuts, input_root))

medians         = []
plus_one_sigma  = []
minus_one_sigma = []
plus_two_sigma  = []
minus_two_sigma = []

green = '#607641' 
yellow = '#F5BB54'

for cut in LxyS_cuts:
    print(' -> LxyS > %.1f' % cut)
    if (LxyS_cuts_file_dict[cut] == "None"):
        minus_two_sigma.append(0.0)
        minus_one_sigma.append(0.0)
        medians.append(0.0)
        plus_one_sigma.append(0.0)
        plus_two_sigma.append(0.0)
        continue
    df_npy = (ROOT.RDataFrame("limit", LxyS_cuts_file_dict[cut])).AsNumpy()
    minus_two_sigma.append(df_npy['limit'][0])
    minus_one_sigma.append(df_npy['limit'][1])
    medians.append(df_npy['limit'][2])
    plus_one_sigma.append(df_npy['limit'][3])
    plus_two_sigma.append(df_npy['limit'][4])
    
print(medians)
medians         = np.asarray(medians)        * 10
plus_one_sigma  = np.asarray(plus_one_sigma) * 10
plus_two_sigma  = np.asarray(plus_two_sigma) * 10
minus_one_sigma = np.asarray(minus_one_sigma)* 10
minus_two_sigma = np.asarray(minus_two_sigma)* 10

fig, ax = plt.subplots()

#ax.step(LxyS_cuts, 
#        medians, 
#        where   ='mid', 
#        ls      = '--',
#        color   = 'k',
#        label   = 'Expected',
#        zorder  =10)
e_lim = ax.errorbar(LxyS_cuts, 
                    medians, 
                    xerr=0.05*np.ones(LxyS_cuts.shape[0]), 
                    fmt='none', 
                    ecolor='k', 
                    zorder = 10)
e_lim[-1][0].set_linestyle('--')

# plot errors as boxes
for i in range(len(LxyS_cuts)):
    # 1 sigma band
    one_sigma = ax.fill_between([LxyS_cuts[i]-0.05, LxyS_cuts[i]+0.05],
                    [minus_one_sigma[i], minus_one_sigma[i]],
                    [plus_one_sigma[i], plus_one_sigma[i]],
                    step = 'mid',
                    color = green,
                    zorder = 3, 
                    )
    # 2 sigma band
    two_sigma = ax.fill_between([LxyS_cuts[i]-0.05, LxyS_cuts[i]+0.05],
                    [minus_two_sigma[i], minus_two_sigma[i]],
                    [plus_two_sigma[i], plus_two_sigma[i]],
                    step = 'mid',
                    color = yellow,
                    zorder = 2,              
    )

# Style
hep.cms.label("Preliminary", data = True, year = 2022)
ax.set_ylim(2.0, 25)
ax.set_ylabel(r'Br($\tau\to 3\mu$) expUL @ 90 % CL (10$^{-8}$)')
ax.set_xlim(LxyS_cuts[0], LxyS_cuts[-1])
ax.set_xlabel(r'Lxy/$\sigma$ cut')
ax.set_xticks(LxyS_cuts)
ax.grid( linestyle='--', linewidth=0.5, zorder=0)

ax.legend([e_lim, one_sigma, two_sigma], ['Expected', 'Expected $\pm 1\sigma$', 'Expected $\pm 2\sigma$'], loc='upper right')
#plt.legend()

plt.savefig('plots/limt_scan_vs_LxyS.png')
plt.savefig('plots/limt_scan_vs_LxyS.pdf')



