import ROOT
ROOT.gStyle.SetOptStat(0)
import cmsstyle as CMS
import mplhep as hep
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

import os
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_AL',                                          )
parser.add_argument('--input_HN',                                          )
parser.add_argument('-o', '--plotout_dir',                                        default = 'WTau3Mu')
parser.add_argument('-d', '--datacard_tag',                                       default = 'WTau3Mu')
parser.add_argument('-n', '--name_combine',                                       default = '/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/Training_kFold_HLT_overlap_LxyS1.5_2024May27/bdt_scan/')
parser.add_argument('-y', '--year',                                                default = '2022')
parser.add_argument('--CL',                 type =float,                           default = 0.90)

args = parser.parse_args()

tree_name = 'limit'
AL_file   = args.input_AL#'/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27_bkgModel/input_combine/Tau3MuCombine.WTau3Mu_A22_BDTscan.AsymptoticLimits.root'
HN_file   = args.input_HN#'/eos/user/c/cbasile/CombineTools/CMSSW_11_3_4/src/WTau3Mu_limits/bdt_cut_optimization/binBDT_LxyS1.5_HLT_overlap_2024May27_bkgModel/input_combine/Tau3MuCombine.WTau3Mu_A22_BDTscan.HybridNew.root'

tag = args.name_combine 
plotout_dir = args.plotout_dir
CMS.SetLumi(f'{args.year}, 34.4')
CMS.SetEnergy('13.6')
legend = CMS.cmsLeg(0.15, 0.70, 0.50, 0.90)

resultsAL_rdf = ROOT.RDataFrame(tree_name, AL_file)
limits_AL = (resultsAL_rdf.Filter('quantileExpected==0.5').AsNumpy())['limit']
resultsHN_rdf = ROOT.RDataFrame(tree_name, HN_file)
limits_HN = (resultsHN_rdf.Filter('quantileExpected==0.5').AsNumpy())['limit']


limitAL_graph = resultsAL_rdf.Filter('quantileExpected==0.5').Graph('bdt_cut', 'limit').GetPtr()
limitAL_graph.SetMarkerColor(ROOT.kBlue)
limitAL_graph.SetMarkerStyle(20)
limitAL_graph.SetLineColor(ROOT.kBlue)
limitAL_graph.SetMarkerSize(1.5)
legend.AddEntry(limitAL_graph, 'AsymptoticLimits')

limitHN_graph = resultsHN_rdf.Filter('quantileExpected==0.5').Graph('bdt_cut', 'limit').GetPtr()
limitHN_graph.SetMarkerColor(ROOT.kRed)
limitHN_graph.SetMarkerStyle(20)
limitHN_graph.SetLineColor(ROOT.kRed)
limitHN_graph.SetMarkerSize(1.5)
legend.AddEntry(limitHN_graph, 'HybridNew')
c = CMS.cmsCanvas(
    'c',
    0.9900 - 0.0005,
    1.0,
    0.9*np.min([np.min(limits_AL), np.min(limits_HN)]),
    1.1*np.max([np.max(limits_AL), np.max(limits_HN)]),
    'BDTcut',f'expUL ({args.CL*100} % CL)',
    square=CMS.kRectangular,extraSpace=0.01,iPos=0.0,scaleLumi=0.80
)
c.cd()
CMS.cmsDraw(limitAL_graph, 
    'LP',
    marker = limitAL_graph.GetMarkerStyle(),
    mcolor = limitAL_graph.GetMarkerColor(), 
    fcolor = limitAL_graph.GetFillColor(),
    fstyle = limitAL_graph.GetFillStyle(), 
)
CMS.cmsDraw(limitHN_graph, 
    'LP same',
    marker = limitHN_graph.GetMarkerStyle(),
    mcolor = limitHN_graph.GetMarkerColor(), 
    fcolor = limitHN_graph.GetFillColor(),
    fstyle = limitHN_graph.GetFillStyle(), 
)
legend.Draw()
c.SaveAs(f'{plotout_dir}/ULscan_BDT_ALvsHN_{tag}.png')
c.SaveAs(f'{plotout_dir}/ULscan_BDT_ALvsHN_{tag}.pdf')