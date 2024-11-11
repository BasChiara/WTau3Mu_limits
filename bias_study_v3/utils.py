import argparse
import ROOT


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_datacard',       dest='input_datacard', type=str,                                      default='input_datacard.txt', help='input datacard')
    parser.add_argument('--mode',                 dest='mode',     choices=['generate','fit_fixed','envelope'],         default="generate", help="[generate,fixed,envelope]")
    parser.add_argument('--gen_func',             dest='gen_func', choices=['expo','const', 'poly1'],                   default="expo", help="wich bkg func to use to generate toys")
    parser.add_argument('--fit_func',             dest='fit_func', choices=['expo','const', 'poly1'],                   default="expo", help="wich bkg func to use to fit toys")
    parser.add_argument('--nToys',                dest='nToys',    type=int,                                            default=1000, help='number of toys to generate')
    parser.add_argument('--nFit',                 dest='nFit',     type=int,                                            default=1000, help='number of toys to generate')
    parser.add_argument('--r_gen',                dest='r_gen',    type=float,                                          default=1.0, help='signal strenght to generate toys')
    parser.add_argument('--tag',                  dest='tag',      type=str,                                            default='', help='tag for the output file')
    parser.add_argument('--dry_run',              dest='dry_run',  action='store_true',                                 help='set to just print the commands')
    return parser


def summary_pull(input_root, ws_name):
    # --- read input root file
    # get workspace
    f = ROOT.TFile(input_root)
    ws = f.Get(ws_name)
    if not ws :
        print(f"[ERROR] workspace {ws_name} not found in {input_root}")
        exit(1)
    fail_rate   = ws['fail_rate'].getVal()
    mean_fit    = ws['mean'].getVal()
    pull_median = ws['pull_median'].getVal()
    pull_mean   = ws['pull_mean'].getVal()

    return fail_rate, mean_fit, pull_median, pull_mean