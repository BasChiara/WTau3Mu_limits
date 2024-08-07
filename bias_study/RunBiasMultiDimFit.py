import ROOT
import os
import utils
import sys
import numpy as np
sys.path.append('..')
import style.color_text as ct

# --- argument pareser
args = (utils.get_arguments()).parse_args()
print('\n')

# --- setup
toy_tag          = f'.gen{args.nToys/1000:,.0f}K{args.gen_func}_{args.tag}_r{args.r_gen:,.1f}'
toys_file_name   = f'toys{toy_tag}'
tau_mass     = 1.777

# --- preliminary checks
# check datacard is compiled
if not args.input_datacard.endswith('.root') :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} datacard {args.input_datacard} must be compiled with text2workspace.py")
    exit(1)
elif not os.path.isfile(args.input_datacard) :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} datacard {args.input_datacard} not found")
    exit(1)

# --- generation step
# generate toys with background function in the datacard and signal strength r_gen
if args.mode == "generate":

    print(f'{ct.color_text.BOLD}[GEN]{ct.color_text.END} {args.nToys} toys with bkg {args.gen_func} \t r = {args.r_gen}')  
    cmd = f'combine -M GenerateOnly -m {tau_mass} -d {args.input_datacard}  --setParameters Mtau={tau_mass} --freezeParameters Mtau,slope --expectSignal {args.r_gen} -n {toy_tag}  --saveToys -t {args.nToys} -s -1\n\n'
    print(cmd)
    if not args.dry_run : os.system(cmd)
    
    # save toys
    if not os.path.isdir('toys') : os.system('mkdir toys')
    cmd = f'mv higgsCombine{toy_tag}* ./toys/{toys_file_name}.root'
    if not args.dry_run : os.system(cmd)
    print(f'{ct.color_text.BOLD}[GEN]{ct.color_text.END} toys saved in ./toys/{toys_file_name}.root')

# --- fit step
# fit toys with background function in the datacard
if args.mode == "fit_fixed":
    # check if toy file exists
    if not os.path.isfile(f'./toys/{toys_file_name}.root') :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} toys file ./toys/{toys_file_name}.root not found")
        exit(1)
    else : toys_file_name = f'./toys/{toys_file_name}.root' 

    fit_tag = f'.gen_{args.gen_func}_fit_{args.fit_func}_{args.tag}_r{args.r_gen:,.1f}'
    print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} {args.nToys} {args.gen_func}-toys with bkg {args.fit_func} \t r = {args.r_gen}')
    cmd = f'combine -M MultiDimFit {args.input_datacard} -m {tau_mass} --freezeParameters Mtau,slope -t {args.nToys} -n {fit_tag} --expectSignal {args.r_gen} --toysFile {toys_file_name}.root --algo singles --rMin 0.01 --rMax {np.min([10*args.r_gen, 20])} \n\n'
    print(cmd)
    if not args.dry_run : os.system(cmd)