import ROOT
ROOT.gROOT.SetBatch(True)

import os
import glob
import argparse
import numpy as np

argparser = argparse.ArgumentParser(description='Plot bias study results')
argparser.add_argument('--fit_func', default='expo', help='Fit function to study the bias')
argparser.add_argument('-c','--cat',  choices=['ABC', 'A', 'B', 'C'], default='ABC',  help='category to process')
argparser.add_argument('-y','--year', choices=['22', '23'], default='22', help='Year to process')
argparser.add_argument('--tag',                              help='Job tag')
argparser.add_argument('--debug', action='store_true', help='Print debug information')
argparser.add_argument('--output', default='bias_study.root', help='Output file name')

args = argparser.parse_args()
print('\n')


# -- CATEGORY --#
categories = []
if args.cat == 'ABC':
    categories =['A', 'B', 'C']
else : categories.append(args.cat)


c = ROOT.TCanvas('c', 'c', 800, 600)
for cat in categories:
    print(f'+ processing category {cat}{args.year}')
    out_tag = f'fit{args.fit_func}_{cat}{args.year}'

    # -- INPUT -- #
    # get all files using the specified fitting fuction
    input_files = f'./fit_results/fitResults_fit{args.fit_func}.gen*_{cat}{args.year}_{args.tag}.root'
    chain = ROOT.TChain('fit_results')
    chain.Add(input_files)
    print('[+] added inpot files :', input_files)
    print('[+] chain entries :', chain.GetEntries())

    nbins, xlow, xup = 45, -1.0, 3.5
    chain.Draw(f'(N_SR_fit/N_SR_gen - 1 )>>N_SR_bias({nbins}, {xlow}, {xup})', '', 'goff')
    N_SR_bias = ROOT.gDirectory.Get('N_SR_bias')
    N_SR_bias.SetDirectory(0)
    N_SR_bias.GetXaxis().SetTitle('N_{SR}^{fit}/N_{SR}^{gen} - 1')
    N_SR_bias.GetYaxis().SetTitle('Entries')
    N_SR_bias.SetLineColor(ROOT.kBlue)
    N_SR_bias.SetLineWidth(2)
    N_SR_bias.SetFillColor(ROOT.kBlue)
    N_SR_bias.SetFillStyle(3004)
    #N_SR_bias.SetStats(1111)
    N_SR_bias.SetTitle(f'fit bias in signal region - {args.fit_func} ({cat}{args.year})')
    N_SR_bias.Draw('hist')
    c.Print(f'plots/bias_SR_{out_tag}.png')
    c.Print(f'plots/bias_SR_{out_tag}.pdf')

    nbins, xlow, xup = 25, -1.0, 1.0
    chain.Draw(f'((Nb_fit + Ns_fit)/(Nb_gen + Ns_gen) - 1 )>>N_FR_bias({nbins}, {xlow}, {xup})', '', 'goff')
    N_FR_bias = ROOT.gDirectory.Get('N_FR_bias')
    N_FR_bias.SetDirectory(0)
    N_FR_bias.GetXaxis().SetTitle('(N_{FR}^{fit})/(N_{FR}^{gen}) - 1')
    N_FR_bias.GetYaxis().SetTitle('Entries')
    N_FR_bias.SetLineColor(ROOT.kRed)
    N_FR_bias.SetLineWidth(2)
    N_FR_bias.SetFillColor(ROOT.kRed)
    N_FR_bias.SetFillStyle(3004)
    #N_FR_bias.SetStats(1111)
    N_FR_bias.SetTitle(f'fit bias in full mass region - {args.fit_func} ({cat}{args.year})')
    N_FR_bias.Draw('hist')
    c.Print(f'plots/bias_FR_{out_tag}.png')
    c.Print(f'plots/bias_FR_{out_tag}.pdf')
    print('[+] output plots saved in plots/')


