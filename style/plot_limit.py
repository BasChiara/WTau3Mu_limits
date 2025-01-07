import ROOT
import argparse
import pandas as pd
import numpy as np
import os
import json

import matplotlib.pyplot as plt
import sys
from color_text import color_text as ct
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)))

def format_limit_latex(categories, median, plus_1sigma, minus_1sigma, plus_2sigma, minus_2sigma ):
    # in 10e-8
    median = [x*10 for x in median]
    plus_1sigma = [x*10 for x in plus_1sigma]
    minus_1sigma = [x*10 for x in minus_1sigma]
    plus_2sigma = [x*10 for x in plus_2sigma]
    minus_2sigma = [x*10 for x in minus_2sigma]
    print("Category & Median & +1$\sigma$ & -1$\sigma$ & +2$\sigma$ & -2$\sigma$ \\\\")
    for i, cat in enumerate(categories):
        #print(f"{cat} & {median[i]:.1f} & {plus_1sigma[i]:.1f} & {minus_1sigma[i]:.1f} & {plus_2sigma[i]:.1f} & {minus_2sigma[i]:.1f} \\\\")
        print(f"{cat} & {median[i]:.1f} \\\\")

def get_limit_from_files(filename, to_pandas = False):
    
    if not os.path.isfile(filename):
        print(f"{ct.RED}[ERROR]{ct.END} file not found: ", filename)
        sys.exit(1)
    limit = ROOT.RDataFrame("limit", filename)
    if to_pandas : limit = pd.DataFrame(limit.AsNumpy())
    return limit

def draw_limit(categories, 
               median, plus_1sigma, minus_1sigma, plus_2sigma, minus_2sigma ,
               output_file, 
               x_title, y_title, 
               log_y, log_x):
    
    point = np.arange(1, len(categories)+1)
    delta = 1
    
    fig, ax = plt.subplots()
    e_lim = ax.errorbar(point, 
                    median, 
                    xerr=0.5, 
                    fmt='none', 
                    ecolor='k', 
                    zorder = 10
    )
    e_lim[-1][0].set_linestyle('--')
    
    for i in range(len(categories)): 
        s1_lim = ax.fill_between(
            [point[i] - delta/2., point[i] + delta/2.], 
            [plus_1sigma[i], plus_1sigma[i]], 
            [minus_1sigma[i], minus_1sigma[i]], 
            step = 'mid',
            color=ct.CMS_green,
            zorder = 5)
        s2_lim = ax.fill_between(
            [point[i] - delta/2., point[i] + delta/2.], 
            [plus_2sigma[i],  plus_2sigma[i]], 
            [minus_2sigma[i], minus_2sigma[i]], 
            step = 'mid',
            color=ct.CMS_yellow,
            zorder = 0)
    ax.set_xticks(point)
    ax.set_xticklabels(categories, rotation=0, ha='center')
    ax.tick_params(axis='both', which='major', labelsize=14) 

    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title, fontsize=14)
    ax.legend([e_lim, s1_lim, s2_lim], 
          ['Expected', 'Expected $\pm 1\sigma$', 'Expected $\pm 2\sigma$'], 
          loc='upper left', fontsize=14, 
          frameon=False) 
    y_range = [0.0, max(plus_2sigma) + 3.0]
    if y_range:
        ax.set_ylim(y_range)
    if log_y:
        ax.set_yscale("log")
    if log_x:
        ax.set_xscale("log")
    plt.savefig(output_file+".png")
    plt.savefig(output_file+".pdf")

    return fig, ax

def get_limit_from_dict(dictionary, output_file, x_title, y_title, log_y, log_x):
    
    categories = dictionary.keys()
    median = []
    plus_1sigma = []
    minus_1sigma = []
    plus_2sigma = []
    minus_2sigma = []

    for cat in dictionary:
        input_file = dictionary[cat]
    
        limit = get_limit_from_files(input_file, to_pandas = True)
        median.append(limit[limit['quantileExpected']==0.5].limit.values[0])
        tolerance = 1e-6
        minus_1sigma.append( limit[abs(limit['quantileExpected']-0.160) < tolerance].limit.values[0])
        plus_1sigma.append(limit[abs(limit['quantileExpected']-0.840) < tolerance].limit.values[0])
        minus_2sigma.append(limit[abs(limit['quantileExpected']-0.025) < tolerance].limit.values[0])
        plus_2sigma.append( limit[abs(limit['quantileExpected']-0.975) < tolerance].limit.values[0])
    
    draw_limit(categories,
                median, plus_1sigma, minus_1sigma, plus_2sigma, minus_2sigma,
                output_file, 
                x_title, y_title, 
                log_y, log_x)
    
    format_limit_latex(categories, median, plus_1sigma, minus_1sigma, plus_2sigma, minus_2sigma)
    
    

def plot_limit_singlefile(input_file, output_file, x_title, y_title, x_range, y_range, log_y, log_x):
    
    file = ROOT.TFile(input_file)
    if not file:
        print(f"{ct.RED}[ERROR]{ct.END} file not found: ", input_file)
        sys.exit(1)
    
    rdf = ROOT.RDataFrame("limit", input_file)
    limit = pd.DataFrame(rdf.AsNumpy())
    print(limit)

    median = []
    plus_1sigma = []
    minus_1sigma = []
    plus_2sigma = []
    minus_2sigma = []

    median.append(limit[limit['quantileExpected']==0.5].limit.values[0])
    plus_1sigma.append(limit[limit['quantileExpected']==0.16].limit.values[0])
    minus_1sigma.append(limit[limit['quantileExpected']==0.84].limit.values[0])
    minus_2sigma.append(limit[limit['quantileExpected']==0.025].limit.values[0])
    plus_2sigma.append(limit[limit['quantileExpected']==0.975].limit.values[0])
    
    
    fig, ax = plt.subplots()
    point = [1]
    delta = 1
    e_lim = ax.errorbar(point, 
                    median, 
                    xerr=0.5, 
                    fmt='none', 
                    ecolor='k', 
                    zorder = 10
    )
    e_lim[-1][0].set_linestyle('--')
    
   
    s1_lim = ax.fill_between(
        [point[0] - delta/2., point[0] + delta/2.], 
        [plus_1sigma[0], plus_1sigma[0]], 
        [minus_1sigma[0], minus_1sigma[0]], 
        step = 'mid',
        color=ct.CMS_green,
        zorder = 5)
    s2_lim = ax.fill_between(
        [point[0] - delta/2., point[0] + delta/2.], 
        [plus_2sigma[0],  plus_2sigma[0]], 
        [minus_2sigma[0], minus_2sigma[0]], 
        step = 'mid',
        color=ct.CMS_yellow,
        zorder = 0)
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.legend()
    if x_range:
        ax.set_xlim(x_range)
    if y_range:
        ax.set_ylim(y_range)
    if log_y:
        ax.set_yscale("log")
    if log_x:
        ax.set_xscale("log")
    plt.savefig(output_file)



parser = argparse.ArgumentParser(description="Plot limit")
parser.add_argument("--input_file", help="Input file")
parser.add_argument("--output", help="Output file")
parser.add_argument("--x_title", help="X axis title", default="")
parser.add_argument("--y_title", help="Y axis title", default=r'Br($\tau\to 3\mu$) expUL @ 90 % CL (10$^{-7}$)')
parser.add_argument("--log_y", help="Log scale on Y axis", action="store_true")
parser.add_argument("--log_x", help="Log scale on X axis", action="store_true")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
    print(f"{ct.RED}[ERROR]{ct.END} input file not provided")
    sys.exit(1)
with open(args.input_file, 'r') as f:
    input_dict = json.load(f)
    print(input_dict)

#plot_limit_singlefile(args.input_file, args.output_file, args.x_title, args.y_title, args.x_range, args.y_range, args.log_y, args.log_x)
get_limit_from_dict(input_dict, args.output, args.x_title, args.y_title, args.log_y, args.log_x)


    