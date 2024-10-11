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
sys.path.append('/afs/cern.ch/user/c/cbasile/WTau3MuRun3_Analysis/CMSSW_13_0_13/src/Tau3MuAnalysis')
from mva.config import LumiVal_plots 

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--inputs',             action='append')
parser.add_argument('-l','--labels',             action='append')
parser.add_argument('-x', '--comp_by',           choices=['bdt_cut', 'expNb'],    default='bdt_cut')
parser.add_argument('--input_sensititvity')
parser.add_argument('-o', '--plotout_dir',                                        default = 'WTau3Mu')
parser.add_argument('-t', '--tag',                                                default = '')
parser.add_argument('-d', '--datacard_tag',                                       default = 'WTau3Mu')
parser.add_argument('-n', '--name_combine',                                       default = '/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_HLT_overlap_LxyS1.5_2024May27/bdt_scan/')
parser.add_argument('-y', '--year',             choices=['2022', '2023'],         default = '2022')
parser.add_argument('-c', '--category',         choices=['A', 'B', 'C'],          default = 'A')
parser.add_argument('--CL',                 type =float,                          default = 0.90)


args = parser.parse_args()
tag = '_'.join([args.comp_by, args.tag, args.name_combine])
plotout_dir = args.plotout_dir
# sanity checks
Nfiles = len(args.inputs)
Nlabels = len(args.labels)
if Nfiles != Nlabels:
    print(f'[ERROR] number of files does NOT match the number of labels -> Nfiles = {Nfiles} / Nlabels = {Nlabels}')
    exit(-1)

tree_name = 'limit'

# setup canvas
CMS.SetLumi(f'{args.year}, {LumiVal_plots[args.year]}')
CMS.SetEnergy('13.6')
CMS.SetExtraText("Preliminary")
CMS.ResetAdditionalInfo()
CMS.AppendAdditionalInfo(f'W#rightarrow#tau(3#mu)#nu CAT {args.category}')
#CMS.SetCMSPalette() NOT working
root_color_list = [ROOT.kBlue, ROOT.kRed, ROOT.kMagenta-7, ROOT.kGreen+2, ROOT.kOrange+7]
legend = CMS.cmsLeg(0.5, 0.70, 0.75, 0.90)

min_BDT_val = 0.9900-0.0005
max_BDT_val = 1.0 

min_lim_val = 100
max_lim_val = 0
graphs = []
for i, f in enumerate(args.inputs):
    print(f'[+] {f}')
    rdf = ROOT.RDataFrame(tree_name, f).Filter('quantileExpected==0.5')
    limits  = rdf.AsNumpy()['limit']
    bdt_cut = rdf.AsNumpy()['bdt_cut']
    min_BDT_val = np.min([min_BDT_val, np.min(bdt_cut)-0.0005])
    min_lim_val = np.min([min_lim_val, np.min(limits)])
    max_lim_val = np.max([max_lim_val, np.max(limits)])

    limit_graph = rdf.Graph(args.comp_by, 'limit').GetPtr()
    limit_graph.SetMarkerColor(root_color_list[i])
    limit_graph.SetMarkerStyle(20)
    limit_graph.SetLineColor(root_color_list[i])
    limit_graph.SetMarkerSize(1.5)
    graphs.append(limit_graph)
    legend.AddEntry(limit_graph, args.labels[i])
print(min_lim_val)
c = CMS.cmsCanvas(
    'c',
    min_BDT_val,
    max_BDT_val,
    0.9*min_lim_val,
    1.1*max_lim_val,
    'BDTcut',f'expUL ({args.CL*100} % CL)',
    square=CMS.kRectangular,extraSpace=0.02,iPos=11,scaleLumi=0.80
)
c.cd()
for i, g in enumerate(graphs):
    CMS.cmsDraw(g, 
    'LP' + ('same' if i > 0 else ''),
    marker = g.GetMarkerStyle(),
    mcolor = g.GetMarkerColor(), 
    fcolor = g.GetFillColor(),
    fstyle = g.GetFillStyle(), 
    )
legend.Draw()
c.SaveAs(f'{plotout_dir}/ULscan_{tag}.png')
c.SaveAs(f'{plotout_dir}/ULscan_{tag}.pdf')

