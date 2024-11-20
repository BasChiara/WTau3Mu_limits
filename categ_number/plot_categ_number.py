import ROOT
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import style.color_text as color_text
import numpy as np
import matplotlib.pyplot as plt

splitting = ['NOsplit', 'splitX2', 'splitX3']

median          = []
plus_one_sigma  = []
minus_one_sigma = []
plus_two_sigma  = []
minus_two_sigma = []

HN_median  = []

for split in splitting:
    input_AL = f'higgsCombine.WTau3Mu_comb22_{split}.AsymptoticLimits.mH120.root'
    rdf_AL = ROOT.RDataFrame('limit', input_AL).AsNumpy()
    print(f'[+] {input_AL}')
    input_HN = f'higgsCombine.WTau3Mu_comb22_{split}.HybridNew.mH120.quant0.500.root'
    rdf_HN = ROOT.RDataFrame('limit', input_HN).AsNumpy()
    print(f'[+] {input_HN}')

    minus_two_sigma.append(rdf_AL['limit'][0])
    minus_one_sigma.append(rdf_AL['limit'][1])
    median.append(rdf_AL['limit'][2])
    plus_one_sigma.append(rdf_AL['limit'][3])
    plus_two_sigma.append(rdf_AL['limit'][4])

    HN_median.append(rdf_HN['limit'][0])
    


fig, ax = plt.subplots()
x = np.arange(len(splitting))
width = 0.5
x_error = width*np.ones(len(splitting))
e_lim = ax.errorbar(x, 
            median, 
            xerr=x_error, 
            fmt='none', 
            ecolor='k', 
            zorder=10)
e_lim[-1][0].set_linestyle('--')

# plot errors as boxes
for i in range(len(splitting)):
    # 1 sigma band
    one_sigma = ax.fill_between([x[i]-width, x[i]+width],
                    [minus_one_sigma[i], minus_one_sigma[i]],
                    [plus_one_sigma[i], plus_one_sigma[i]],
                    step = 'mid',
                    color = color_text.color_text.CMS_green,
                    zorder = 3, 
                    )
    # 2 sigma band
    two_sigma = ax.fill_between([x[i]-width, x[i]+width],
                    [minus_two_sigma[i], minus_two_sigma[i]],
                    [plus_two_sigma[i], plus_two_sigma[i]],
                    step = 'mid',
                    color = color_text.color_text.CMS_yellow,
                    zorder = 2,              
    )
hn_lim = ax.errorbar(x, 
            HN_median, 
            xerr=x_error, 
            fmt='none', 
            ecolor='r', 
            zorder=10)
hn_lim[-1][0].set_linestyle('--')

ax.legend([e_lim, one_sigma, two_sigma, hn_lim], 
          ['Expected', 'Expected $\pm 1\sigma$', 'Expected $\pm 2\sigma$', 'HybridNew'], 
          loc='upper right', fontsize=14, 
          frameon=False) 

ax.set_ylabel(r'95% CL limit $Br(\tau \rightarrow 3\mu) \times 10^{-7}$', fontdict={'size': 14})
ax.set_ylim(0, 4.0)
ax.set_xticks(x)
ax.set_xticklabels(splitting)
plt.savefig('AL_vs_HN.png')


