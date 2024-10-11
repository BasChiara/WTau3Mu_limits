import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.EnableImplicitMT()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplhep as hep

LxyS_cuts = np.asarray(range(13, 32)) / 10.
root_tag = 'Optuna_HLT_overlap_2024Jul'
outfile = 'higgsCombine.WTau3Mu_full22.AsymptoticLimits.mH120.root'
plot_name = f'plots/limt_scan_vs_LxyS_{root_tag}'
input_root = {
    #0.0: f'binBDT_LxyS0.0_{root_tag}/{outfile}',
    1.4: f'binBDT_LxyS1.4_{root_tag}12/{outfile}',
    1.5: f'binBDT_LxyS1.5_{root_tag}26/{outfile}',
    1.7: f'binBDT_LxyS1.7_{root_tag}12/{outfile}',
    1.9: f'binBDT_LxyS1.9_{root_tag}12/{outfile}',
    2.0: f'binBDT_LxyS2.0_{root_tag}16/{outfile}',
    2.1: f'binBDT_LxyS2.1_{root_tag}11/{outfile}',
    3.0: f'binBDT_LxyS3.0_{root_tag}26/{outfile}',
}

LxyS_cuts_file_dict = input_root#dict(zip(LxyS_cuts, input_root))

medians         = []
plus_one_sigma  = []
minus_one_sigma = []
plus_two_sigma  = []
minus_two_sigma = []

green = '#607641' 
yellow = '#F5BB54'

for cut in LxyS_cuts:
    try:
        print(' -> LxyS > %.1f in %s' % (cut, LxyS_cuts_file_dict[cut]))
    except:
        print(' -> NO file for LxyS > %.1f' % cut)
        medians.append(0.0)
        plus_one_sigma.append(0.0)
        plus_two_sigma.append(0.0)
        minus_one_sigma.append(0.0)
        minus_two_sigma.append(0.0)
        continue
    df_npy = (ROOT.RDataFrame("limit", LxyS_cuts_file_dict[cut])).AsNumpy()
    df_npy = pd.DataFrame(df_npy)
    start = 0
    print(f' median: {df_npy[df_npy.quantileExpected == 0.50].limit.values[0]} -1sigma: {df_npy[df_npy.quantileExpected == 0.160].limit.values[0]} +1sigma: {df_npy[df_npy.quantileExpected == 0.840].limit.values[0]}')
    minus_two_sigma.append(df_npy[df_npy.quantileExpected == 0.025].limit.values[0])
    minus_one_sigma.append(df_npy[df_npy.quantileExpected == 0.160].limit.values[0])
    medians.append(df_npy[df_npy.quantileExpected == 0.50].limit.values[0])
    plus_one_sigma.append(df_npy[df_npy.quantileExpected == 0.840].limit.values[0])
    plus_two_sigma.append(df_npy[df_npy.quantileExpected == 0.975].limit.values[0])


print(medians)
medians         = np.asarray(medians)        * 10
plus_one_sigma  = np.asarray(plus_one_sigma) * 10
plus_two_sigma  = np.asarray(plus_two_sigma) * 10
minus_one_sigma = np.asarray(minus_one_sigma)* 10
minus_two_sigma = np.asarray(minus_two_sigma)* 10

fig, ax = plt.subplots()

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
hep.cms.label("Preliminary", data = True, year = 2022, ax = ax)
ax.set_ylim(2.0, 25)
ax.set_ylabel(r'Br($\tau\to 3\mu$) expUL @ 90 % CL (10$^{-8}$)', fontsize=16)
ax.set_xlim(LxyS_cuts[0], LxyS_cuts[-1])
ax.set_xlabel(r'Lxy/$\sigma$ cut', fontsize=16)
ax.set_xticks(LxyS_cuts[::2])
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid( linestyle='--', linewidth=0.5, zorder=0)

ax.legend([e_lim, one_sigma, two_sigma], 
          ['Expected', 'Expected $\pm 1\sigma$', 'Expected $\pm 2\sigma$'], 
          loc='upper right', fontsize=14, 
          frameon=False) 
#plt.legend()

plt.savefig(plot_name + '.png')
plt.savefig(plot_name + '.pdf')



