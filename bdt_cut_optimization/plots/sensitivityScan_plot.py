import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use([hep.style.ROOT, hep.style.CMS])

import os
import numpy as np

import sys
#sys.path.append('/afs/cern.ch/user/c/cbasile/WTau3MuRun3_Analysis/CMSSW_13_0_13/src/Tau3MuAnalysis')
#from mva.config import LumiVal_plots 

LumiVal_plots = {
    '2022preEE'     : "13.6",
    '2022EE'        : "20.8",
    '2022'          : "34.5", 
    '2023preBPix'   : "18.0",
    '2023BPix'      : "9.7",
    '2023'          : "27.7",
    '2024'          : "108.4",
    '2024early'     : "56.1",
    '2024late'      : "57.9",
    '2024B'         : "0.13",
    '2024C'         : "7.24",
    '2024D'         : "7.96",
    '2024E'         : "11.32",
    '2024F'         : "29.45",
    '2024G'         : "40.08",
    '2024H'         : "5.79",
    '2024I'         : "12.07",
    'Run3'          : "170.6",#"62.2",
}

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_sensitivity',
                    help='input sensitivity scan .root file')
parser.add_argument('--input_limits',
                    help='input sensitivity scan .root file')
parser.add_argument('-x', '--comp_by',
                    choices=['bdt_cut', 'expNb'],
                    default='bdt_cut')
parser.add_argument('-o', '--plotout_dir',
                    default = 'WTau3Mu')
parser.add_argument('-t', '--tag',
                    default = '')
parser.add_argument('-y', '--year',
                    choices=['2022', '2023', '2024', '2024early', '2024late'],
                    default = '2022')
parser.add_argument('-c', '--category',
                    choices=['A', 'B', 'C'],
                    default = 'A')
parser.add_argument('--CL',
                    type =float,
                    default = 0.90)


args = parser.parse_args()

# - OUTPUT
tag = '_'.join([args.comp_by, args.tag])
plotout_dir = args.plotout_dir
if not os.path.exists(plotout_dir):
    os.makedirs(plotout_dir)

# - INPUT
# read sensitivity tree
srdf = ROOT.RDataFrame("sensitivity_tree", args.input_sensitivity)
punzi = srdf.AsNumpy()['PunziS_val']
S = srdf.AsNumpy()['sig_Nexp']
B = srdf.AsNumpy()['bkg_Nexp_Sregion']
soverrootb = []
[soverrootb.append(s/b**0.5 if b>0 else 0) for s,b in zip(S,B)]
argmax_punzi = np.argmax(punzi)
# read limit tree
lrdf = ROOT.RDataFrame('limit', args.input_limits).Filter('quantileExpected==0.5')
if not lrdf:
    print(f'[ERROR] no limit tree found in {args.input_limits}')
    exit(-1)
limit  = lrdf.AsNumpy()['limit']
argmin_limit = np.argmin(limit)
bdt_cut = lrdf.AsNumpy()['bdt_cut']

print(f'[INFO] max Punzi {punzi[argmax_punzi]:.3f} at BDT cut {bdt_cut[argmax_punzi]:.3f}')
print(f'[INFO] min limit {limit[argmin_limit]:.3f} at BDT cut {bdt_cut[argmin_limit]:.3f}')
# === PLOT ===
fig, ax1 = plt.subplots(figsize=(10, 8))

# First axis: Limit vs BDT cut
ax1.set_xlabel("BDT cut")
ax1.set_ylabel("exp. UL @ 90% CL (x$10^{-7}$)")
ax1.plot(bdt_cut, limit, marker='o', linestyle='-', color="blue", label="Exp. UL")
ax1.tick_params(axis='y')
ax1.set_xticks(bdt_cut)
ax1.set_xticklabels([f"{x:.3f}" for x in bdt_cut], rotation=45)
ax1.text(0.05, 0.75, f'CAT {args.category}', transform=ax1.transAxes, fontsize=25)

# Second axis: Punzi significance vs BDT cut
ax2 = ax1.twinx()
ax2.set_ylabel("Punzi significance")
ax2.plot(bdt_cut, punzi, marker='s', linestyle='--', color="red", label="Punzi")
ax2.tick_params(axis='y')

# Add CMS text
hep.cms.text("Preliminary", loc=0, ax=ax1)
hep.cms.lumitext(f"{args.year}, {LumiVal_plots[args.year]}"+" fb$^{-1}$" , ax=ax1)
plt.title("")
ax1.grid(True)

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
name = f"Limit_Punzi_vs_BDTCut_{tag}.png"
plt.savefig(name)
print(f"[INFO] Plot saved as {name}")

# Prepare lists to store values
#bdt_cuts = []
#soverrootb = []
#punzi = []
#
## Loop over tree entries
#for entry in tree:
#    bdt_cut = entry.bdt_cut
#    S = entry.sig_Nexp
#    B = entry.bkg_Nexp_Sregion
#
#    # Avoid division by zero
#    if B > 0: S_over_sqrt_B = S / np.sqrt(B)
#    else:     S_over_sqrt_B = 0
#
#    bdt_cuts.append(bdt_cut)
#    soverrootb.append(S_over_sqrt_B)
#    punzi.append(entry.PunziS_val)

# normalize to max
soverrootb = np.array(soverrootb)/np.max(soverrootb)
punzi = np.array(punzi)/np.max(punzi)

# Plotting
plt.figure(figsize=(8,6))
plt.plot(bdt_cut, soverrootb, marker='o', label='S / √B', color='blue')
plt.plot(bdt_cut, punzi, marker='o', label='Punzi', color='red')
plt.xlabel("BDT Cut")
plt.ylabel("normalized significance ") 
plt.xticks(bdt_cut, rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"SoverSqrtB_vs_BDTCut_{tag}.png")
