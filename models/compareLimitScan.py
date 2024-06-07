import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
import cmsstyle as CMS
import mplhep as hep
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

import os
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--inputs',             action='append')
parser.add_argument('-l','--labels',             action='append')
parser.add_argument('-x', '--comp_by',      choices=['bdt_cut', 'expNb'],         default='bdt_cut')
parser.add_argument('--input_sensititvity')
parser.add_argument('-o', '--plotout_dir',                                        default = 'WTau3Mu')
parser.add_argument('-t', '--tag',                                                default = '')
parser.add_argument('-d', '--datacard_tag',                                       default = 'WTau3Mu')
parser.add_argument('-n', '--name_combine',                                       default = '/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_HLT_overlap_LxyS1.5_2024May27/bdt_scan/')
parser.add_argument('-y', '--year',                                               default = '2022')
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
CMS.SetLumi(f'{args.year}, 34.4')
CMS.SetEnergy('13.6')
CMS.SetExtraText("Preliminary")
CMS.ResetAdditionalInfo()
CMS.AppendAdditionalInfo(args.datacard_tag)
#CMS.SetCMSPalette() NOT working
root_color_list = [ROOT.kBlue, ROOT.kRed, ROOT.kMagenta-7, ROOT.kGreen+2, ROOT.kOrange+7]
legend = CMS.cmsLeg(0.5, 0.70, 0.75, 0.90)

min_lim_val = []
max_lim_val = []
graphs = []
for i, f in enumerate(args.inputs):
    print(f'[+] {f}')
    rdf = ROOT.RDataFrame(tree_name, f).Filter('quantileExpected==0.5')
    limits = rdf.AsNumpy()['limit']
    min_lim_val.append(np.min(limits))
    max_lim_val.append(np.max(limits))

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
    0.9900 - 0.0005,
    1.0,
    0.9*np.min(min_lim_val),
    1.1*np.max(max_lim_val),
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

#AL_file   = args.input_AL#'/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27_bkgModel/input_combine/Tau3MuCombine.WTau3Mu_A22_BDTscan.AsymptoticLimits.root'
#HN_file   = args.input_HN#'/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27_bkgModel/input_combine/Tau3MuCombine.WTau3Mu_A22_BDTscan.HybridNew.root'

#resultsAL_rdf = ROOT.RDataFrame(tree_name, AL_file)
#limits_AL = (resultsAL_rdf.Filter('quantileExpected==0.5').AsNumpy())['limit']
#resultsHN_rdf = ROOT.RDataFrame(tree_name, HN_file)
#limits_HN = (resultsHN_rdf.Filter('quantileExpected==0.5').AsNumpy())['limit']
#
#
#limitAL_graph = resultsAL_rdf.Filter('quantileExpected==0.5').Graph('bdt_cut', 'limit').GetPtr()
#limitAL_graph.SetMarkerColor(ROOT.kBlue)
#limitAL_graph.SetMarkerStyle(20)
#limitAL_graph.SetLineColor(ROOT.kBlue)
#limitAL_graph.SetMarkerSize(1.5)
#legend.AddEntry(limitAL_graph, 'AsymptoticLimits')
#
#limitHN_graph = resultsHN_rdf.Filter('quantileExpected==0.5').Graph('bdt_cut', 'limit').GetPtr()
#limitHN_graph.SetMarkerColor(ROOT.kRed)
#limitHN_graph.SetMarkerStyle(20)
#limitHN_graph.SetLineColor(ROOT.kRed)
#limitHN_graph.SetMarkerSize(1.5)
#legend.AddEntry(limitHN_graph, 'HybridNew')
#
#CMS.cmsDraw(limitAL_graph, 
#    'LP',
#    marker = limitAL_graph.GetMarkerStyle(),
#    mcolor = limitAL_graph.GetMarkerColor(), 
#    fcolor = limitAL_graph.GetFillColor(),
#    fstyle = limitAL_graph.GetFillStyle(), 
#)
#CMS.cmsDraw(limitHN_graph, 
#    'LP same',
#    marker = limitHN_graph.GetMarkerStyle(),
#    mcolor = limitHN_graph.GetMarkerColor(), 
#    fcolor = limitHN_graph.GetFillColor(),
#    fstyle = limitHN_graph.GetFillStyle(), 
#)
#legend.Draw()
#c.SaveAs(f'{plotout_dir}/ULscan_BDT_ALvsHN_{tag}.png')
#c.SaveAs(f'{plotout_dir}/ULscan_BDT_ALvsHN_{tag}.pdf')