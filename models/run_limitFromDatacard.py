import os
import numpy as np
import argparse
# custom libraries
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from mva.config import LumiVal_plots 
import utils.combine_utils as Cutils
import style.color_text as ct


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_datacard',                                                help = 'input datacard to feed to combine', required = True)
parser.add_argument('-w', '--working_dir',                                                  help = 'working directory to store the output', required = True)
parser.add_argument('-s', '--step',         choices = ['limit', 'merge', 'plot', 'all'],    default = 'all')
parser.add_argument('-n', '--name_combine',                                                 help = 'tag for combine outputs', default = 'WTau3Mu_A22')
parser.add_argument('-M', '--method',       choices = ['AsymptoticLimits', 'HybridNew'],    default = 'AsymptoticLimits')
parser.add_argument('-T', '--nToys',                                                        help = 'in HybridNew mode is the number of toys', default = 10000)
parser.add_argument('--CL',                    type =float,                                 default = 0.90)
parser.add_argument('-q', '--quantileExpected',type =float,                                 default = 0.500)

args = parser.parse_args()
debug = False

# check if the input datacard exists
if not os.path.exists(args.input_datacard):
    print(f'{ct.color_text.RED}INFO{ct.color_text.END}: input datacard {args.input_datacard} does not exist')
    sys.exit(1)
datacard = args.input_datacard
# check if the working directory exists
if not os.path.exists(args.working_dir):
    os.makedirs(args.working_dir)
    print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: created working directory {args.working_dir}')
else:
    print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: using working directory {args.working_dir}')

# compile the datacard and run combine
if args.step in ['limit', 'all']:

    print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: running combine for datacard {datacard}')
    # compile datacard if it is not already compiled
    if datacard.endswith('.txt'):
        print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: compiling datacard {datacard}')
        datacard = Cutils.compile_datacard(datacard)
    else:
        print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: using compiled datacard {datacard}')

    # run combine
    print(f'{ct.color_text.BOLD}INFO{ct.color_text.END}: running combine for datacard {datacard}')
    Cutils.run_limit(
        datacard, 
        out_name = args.name_combine, 
        output_dir = args.working_dir, 
        method = args.method, 
        CL = args.CL, 
        quantileExpected = args.quantileExpected,
        n_toys=args.nToys,
    )
    