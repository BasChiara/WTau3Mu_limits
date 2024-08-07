# estimate bias from significance [HIG-22-012]
# !! this is a modified version of the original script[1] with no MultiPdf
#   [1] > https://github.com/cms-analysis/flashggFinalFit/tree/dev_fggfinalfits_lite/Combine/Checks/Bias_in_significance

import ROOT
import os
import glob
import re
from optparse import OptionParser
import subprocess
import json

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def get_options():
    parser = OptionParser()
    parser.add_option('--inputWSFile',          dest='inputWSFile',                                                 default='Datacard.root', help="Input workspace")
    parser.add_option('--input_datacard',       dest='input_datacard',                                              default='Datacard.root', help="Input compiled datacard")
    parser.add_option('--tag',                  dest='tag',                                                         default='WTau3Mu_A22',   help="Input compiled datacard")
    parser.add_option('--MH',                   dest='MH',                                                          default='1.777', help="MH -> Mtau")
    parser.add_option('--initial-fit-param',    dest='initial_fit_param',                                           default='lumi_13TeV_uncorrelated_2016', help="Initial fit parameter (combine must have an input parameter to fit to, pick any low impact nuisance)")
    parser.add_option('--nToys',                dest='nToys',                                                       default=2000, type='int', help="Number of toys")
    parser.add_option('--mode',                 dest='mode',     choices=['generate','fixed', 'envelope'],          default="generate", help="[setup,generate,fixed,envelope]")
    parser.add_option('--gen_func',             dest='gen_func', choices=['expo','const', 'poly1'],                 default="expo", help="wich bkg func to use to generate toys")
    parser.add_option('--fit_func',             dest='fit_func', choices=['expo','const', 'poly1'],                 default="expo", help="wich bkg func to use to fit toys")
    parser.add_option('--dry_run',              dest='dry_run',  action='store_true',                               help='set to just print the commands')
    return parser.parse_args()
(opt,args) = get_options()

toy_tag          = f'.gen{opt.nToys/1000:,.0f}K{opt.gen_func}_{opt.tag}'
toys_file_name   = f'toys{toy_tag}'

# I am not using it
#  ----- find the best background fit function with descrete profiling
#if opt.mode == "setup":

#    # Get list of pdfindeices
#    f = ROOT.TFile(opt.inputWSFile)
#    w = f.Get("w")
#    cats = w.allCats()
#    pdf_index = []
#    for cat in rooiter(cats):
#        if "pdfindex" in cat.GetName(): pdf_index.append(cat.GetName()) 
#    f.Close()
   
#    # Initial fit fixing params to be zero
#    cmd = "combine -m %s -d %s -M MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s,r=0 --freezeParameters MH,r -P %s -n _initial --saveWorkspace --saveSpecifiedIndex %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2; cd .."%(opt.MH,opt.inputWSFile,opt.MH,opt.initial_fit_param,",".join(pdf_index))
#    print(cmd)
#    os.system(cmd)

#    # Save best fit pdf indices to json file
#    f_res = ROOT.TFile("higgsCombine_initial.MultiDimFit.mH%s.root"%opt.MH)
#    t = f_res.Get("limit")
#    t.GetEntry(0)
#    pdf_index_bf = {}
#    for index in pdf_index: pdf_index_bf[index] = getattr(t,index)
#    f_res.Close()
#    with open("pdfindex.json","w") as jf:
#        json.dump(pdf_index_bf, jf)

# --- generate nToys toys with the background function in the datacard
if opt.mode == "generate":
    
    cmd = f'combine -m {opt.MH} -d {opt.input_datacard} -M GenerateOnly --setParameters Mtau={opt.MH} --freezeParameters Mtau --expectSignal 0 -n {toy_tag}  --saveToys -t {opt.nToys} -s -1\n\n'
    print(cmd)
    if not opt.dry_run : os.system(cmd)
    if not os.path.isdir('/toys') : os.system('mkdir toys')
    cmd = f'mv higgsCombine{toy_tag}* ./toys/{toys_file_name}.root'
    if not opt.dry_run : os.system(cmd)

if opt.mode == "fixed":

    fit_tag = f'.gen_{opt.gen_func}_fit_{opt.fit_func}_{opt.tag}'
    cmd = f'combine -m {opt.MH} -d {opt.input_datacard} -M Significance --cminDefaultMinimizerStrategy 0 --setParameters Mtau={opt.MH} --expectSignal 0 --freezeParameters Mtau -n {fit_tag} -t {opt.nToys} --toysFile toys/{toys_file_name}.root -s -1\n\n'
    print(cmd)
    if not opt.dry_run : os.system(cmd)

#if opt.mode == "envelope":
#
#    cmd = "combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M Significance --snapshotName MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s --expectSignal 0 --freezeParameters MH -n _envelope_ -t %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --toysFile toys.root --X-rtd ADDNLL_RECURSIVE=1; mv higgsCombine_envelope_* fit_envelope.root"%(opt.MH,opt.MH,opt.MH,opt.nToys)
#    print(cmd)
#    os.system(cmd)
#
