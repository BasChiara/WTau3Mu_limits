import os
import math
from optparse import OptionParser
import json
import numpy as np
import pandas as pd
import uproot
import matplotlib
import glob
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (12.5,10)

def get_options():
    parser = OptionParser()
    parser.add_option('--gen_func',             dest='gen_func', choices=['expo','const', 'poly1'],                 default="expo",          help="wich bkg func to use to generate toys")
    parser.add_option('--fit_func',             dest='fit_func', choices=['expo','const', 'poly1'],                 default="expo",          help="wich bkg func to use to fit toys")
    parser.add_option('--tag',                  dest='tag',                                                         default='WTau3Mu_A22',   help="Input compiled datacard")
    parser.add_option('--bdt_cut',              dest='bdt_cut',  type=float,                                        default=0.9900,          help="Input compiled datacard")
    parser.add_option('--use-mplhep', dest='use_mplhep', default=False, action="store_true")
    return parser.parse_args()
(opt,args) = get_options()

if opt.use_mplhep:
    import mplhep
    mplhep.style.use("CMS")

if not os.path.isdir("plots"): os.system("mkdir plots")

file_dict = {
    "expo" : 'higgsCombine.gen_%s_fit_expo_%s_bdt%.4f.Significance.mH1.777.root' %(opt.gen_func, opt.tag, opt.bdt_cut),
    "const": 'higgsCombine.gen_%s_fit_const_%s_bdt%.4f.Significance.mH1.777.root'%(opt.gen_func, opt.tag, opt.bdt_cut),
    "poly1": 'higgsCombine.gen_%s_fit_poly1_%s_bdt%.4f.Significance.mH1.777.root'%(opt.gen_func, opt.tag, opt.bdt_cut),
    "envelope":"fit_envelope.root"
}

Z_points = np.linspace(0,3,100)
# Z score in gaussian approximation
p_gaus = []
for Z in Z_points: p_gaus.append( (1-math.erf(Z/math.sqrt(2)))/2 )
p_gaus = np.array( p_gaus )

z_thr = 4

# Make figure for all plots
fig = plt.figure( figsize=(12,12) )

f_expo = uproot.open(file_dict['expo'])
f_const = uproot.open(file_dict['const'])
f_poly1 = uproot.open(file_dict['poly1'])
#f_envelope = uproot.open(file_dict['envelope'])

z_expo  = np.array( f_expo['limit'].arrays('limit')['limit'] )
z_const = np.array( f_const['limit'].arrays('limit')['limit'] )
z_poly1 = np.array( f_poly1['limit'].arrays('limit')['limit'] )
#z_envelope = np.array( f_envelope['limit'].arrays('limit')['limit'] )

# Drop failed fits with incorrect Z values
z_expo = z_expo[z_expo<z_thr]
z_const = z_const[z_const<z_thr]
z_poly1 = z_poly1[z_poly1<z_thr]
#z_envelope = z_envelope[z_envelope<z_thr]

N_expo     = len(z_expo)
print("N_expo = %g"%(N_expo))
N_const    = len(z_const)
print("N_const = %g"%(N_const))
N_poly1    = len(z_poly1)
print("N_poly1 = %g"%(N_poly1))
#N_envelope  = len(z_envelope)

#print("N_expo = %g, N_envelope = %g"%(N_expo,N_envelope))

p_expo, p_const, p_poly1= [], [], []
err_expo, err_const, err_poly1 = [], [], []
for Z in Z_points:
    k_expo  = np.sum(z_expo >Z, dtype='float')
    p_expo.append( k_expo/N_expo )
    k_const = np.sum(z_const>Z, dtype='float')
    p_const.append( k_const/N_const )
    k_poly1 = np.sum(z_poly1>Z, dtype='float')
    p_poly1.append( k_poly1/N_poly1 )
    # Bayesian error estimate for efficiency
    err_expo.append( np.sqrt( (((k_expo+1)*(k_expo+2))/((N_expo+2)*(N_expo+3))) - (((k_expo+1)*(k_expo+1))/((N_expo+2)*(N_expo+2))) ) )
    err_const.append( np.sqrt( (((k_const+1)*(k_const+2))/((N_const+2)*(N_const+3))) - (((k_const+1)*(k_const+1))/((N_const+2)*(N_const+2))) ) )
    err_poly1.append( np.sqrt( (((k_poly1+1)*(k_poly1+2))/((N_poly1+2)*(N_poly1+3))) - (((k_poly1+1)*(k_poly1+1))/((N_poly1+2)*(N_poly1+2))) ) )
    #err_envelope.append( np.sqrt( (((k_envelope+1)*(k_envelope+2))/((N_envelope+2)*(N_envelope+3))) - (((k_envelope+1)*(k_envelope+1))/((N_envelope+2)*(N_envelope+2))) ) )

p_expo = np.array( p_expo )
p_const = np.array( p_const )
p_poly1 = np.array( p_poly1 )
print('[i] expo ', p_expo[10])
print('[i] const', p_const[10])
#p_envelope = np.array( p_envelope )
err_expo = np.array( err_expo )
err_const = np.array( err_const )
err_poly1 = np.array( err_poly1 )
#err_envelope = np.array( err_envelope )

p_ref   = np.array([1])
err_ref = np.array([1])
if (opt.gen_func == 'expo') :
    print('[i] ref function is expo')
    p_ref  = p_expo 
    err_ref = err_expo
if (opt.gen_func == 'const') :
    print('[i] ref function is const')
    p_ref  = p_const
    err_ref = err_const
if (opt.gen_func == 'poly1') :
    print('[i] ref function is poly1')
    p_ref  = p_poly1 
    err_ref = err_poly1

axs = []
left, width=0.08,0.82
bottom = 0.1
height = 0.18
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)
bottom = 0.32
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)
height = 0.4
bottom = 0.55
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)

axs[0].plot(Z_points, p_expo/p_ref, ls="-", color='red', linewidth=2 )
axs[0].fill_between(Z_points, (p_expo-err_expo)/p_ref, (p_expo+err_expo)/p_ref,  color='salmon', alpha=0.2 )
axs[0].plot(Z_points, p_const/p_ref, ls="-", color='mediumblue', linewidth=2 )
axs[0].fill_between(Z_points, (p_const-err_const)/p_ref, (p_const+err_const)/p_ref,  color='cornflowerblue', alpha=0.2 )
axs[0].plot(Z_points, p_poly1/p_ref, ls="-", color='seagreen', linewidth=2 )
axs[0].fill_between(Z_points, (p_poly1-err_poly1)/p_ref, (p_poly1+err_poly1)/p_ref,  color='mediumseagreen', alpha=0.2 )

axs[0].fill_between(Z_points, 0.8, 0.9,  color='orange', alpha=0.2 )
axs[0].fill_between(Z_points, 0.9, 1.1,  color='limegreen', alpha=0.2, label="$<10$%" )
axs[0].fill_between(Z_points, 1.1, 1.2,  color='orange', alpha=0.2, label="$<20$%" )
axs[0].legend(loc="upper left", fontsize=12, frameon=True)

axs[0].set_ylim(0.5,1.5)
axs[0].set_xlim(0,2.5)

axs[0].set_ylabel("Ratio to %s"%opt.gen_func, fontsize=16)
axs[0].set_xlabel("Z-score", fontsize=20)


axs[1].plot(Z_points, p_expo/p_gaus, ls="-", color='red', linewidth=2 )
axs[1].fill_between(Z_points, (p_expo-err_expo)/p_gaus, (p_expo+err_expo)/p_gaus,  color='salmon', alpha=0.2 )
axs[1].plot(Z_points, p_const/p_gaus, ls="-", color='mediumblue', linewidth=2 )
axs[1].fill_between(Z_points, (p_const-err_const)/p_gaus, (p_const+err_const)/p_gaus,  color='cornflowerblue', alpha=0.2 )
axs[1].plot(Z_points, p_poly1/p_gaus, ls="-", color='seagreen', linewidth=2 )
axs[1].fill_between(Z_points, (p_poly1-err_poly1)/p_gaus, (p_poly1+err_poly1)/p_gaus,  color='mediumseagreen', alpha=0.2 )
axs[1].plot(Z_points, p_gaus/p_gaus, ls="--", color='black', linewidth=2 )

axs[1].fill_between(Z_points, 0.8, 0.9,  color='orange', alpha=0.2 )
axs[1].fill_between(Z_points, 0.9, 1.1,  color='limegreen', alpha=0.2, label="$<10$%" )
axs[1].fill_between(Z_points, 1.1, 1.2,  color='orange', alpha=0.2, label="$<20$%" )
axs[1].legend(loc="upper left", fontsize=12, frameon=True)


axs[1].set_ylim(0.5,1.5)
axs[1].set_xlim(0,2.5)

axs[1].set_ylabel("Ratio to Gaussian", fontsize=16)
axs[1].set_xticklabels(labels=[], fontsize=0)

axs[2].set_title(opt.tag + "   BDTscore > %.4f"%(opt.bdt_cut), fontsize=16)
axs[2].plot(Z_points, 100*p_expo, ls="-", label="Toys (expo)", color='red', linewidth=2 )
axs[2].fill_between(Z_points, 100*(p_expo-err_expo), 100*(p_expo+err_expo),  color='salmon', alpha=0.2 )
axs[2].plot(Z_points, 100*p_const, ls="-", label="Toys (const)", color='mediumblue', linewidth=2 )
axs[2].fill_between(Z_points, 100*(p_const-err_const), 100*(p_const+err_const),  color='cornflowerblue', alpha=0.2 )
axs[2].plot(Z_points, 100*p_poly1, ls="-", label="Toys (poly1)", color='seagreen', linewidth=2 )
axs[2].fill_between(Z_points, 100*(p_poly1-err_poly1), 100*(p_poly1+err_poly1),  color='mediumseagreen', alpha=0.2 )
axs[2].plot(Z_points, 100*p_gaus, ls="--", label="Gaussian", color='black', linewidth=2, alpha=0.8 )

axs[2].set_ylim(0.1,100)
axs[2].set_xlim(0,2.5)
axs[2].set_yscale("log")

axs[2].set_ylabel("Type-1 error rate [%]", fontsize=20)
axs[2].legend(loc='best', fontsize=16, frameon=True)

fig.savefig('plots/gen_%s_summarySignificance_%s_bdt%.4f.pdf'%(opt.gen_func, opt.tag, opt.bdt_cut), bbox_inches="tight")
fig.savefig('plots/gen_%s_summarySignificance_%s_bdt%.4f.png'%(opt.gen_func, opt.tag, opt.bdt_cut))

axs[1].clear()
axs[2].clear()

fig.clf()
