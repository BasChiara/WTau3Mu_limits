import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
import cmsstyle as CMS
import mplhep as hep
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

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
parser.add_argument('-i','--input',
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

# setup canvas
CMS.SetLumi(f'{args.year}, {LumiVal_plots[args.year]}')
CMS.SetEnergy('13.6')
CMS.SetExtraText("Preliminary")
CMS.ResetAdditionalInfo()
CMS.AppendAdditionalInfo(f'W#rightarrow#tau(3#mu)#nu CAT {args.category}')

# Load ROOT file
file = ROOT.TFile(args.input, "READ")
tree = file.Get("sensitivity_tree")

# Prepare lists to store values
bdt_cuts = []
soverrootb = []
punzi = []

# Loop over tree entries
for entry in tree:
    bdt_cut = entry.bdt_cut
    S = entry.sig_Nexp
    B = entry.bkg_Nexp_Sregion

    # Avoid division by zero
    if B > 0: S_over_sqrt_B = S / np.sqrt(B)
    else:     S_over_sqrt_B = 0

    bdt_cuts.append(bdt_cut)
    soverrootb.append(S_over_sqrt_B)
    punzi.append(entry.PunziS_val)

# normalize to max
soverrootb = np.array(soverrootb)/np.max(soverrootb)
punzi = np.array(punzi)/np.max(punzi)

# Plotting
plt.figure(figsize=(8,6))
plt.plot(bdt_cuts, soverrootb, marker='o', label='S / √B', color='blue')
plt.plot(bdt_cuts, punzi, marker='o', label='Punzi', color='red')
plt.xlabel("BDT Cut")
plt.ylabel("normalized significance ") 
plt.xticks(bdt_cuts, rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"SoverSqrtB_vs_BDTCut_{tag}.png")
