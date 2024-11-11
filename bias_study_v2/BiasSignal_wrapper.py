import utils
import numpy as np
import os
import sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import style.color_text as ct
import mva.config as config


argparser = argparse.ArgumentParser()
argparser.add_argument('--dry_run',         action='store_true', help='set to just print the commands')
argparser.add_argument('--store_dir',       default='./', help='directory to store the results')
argparser.add_argument('--do_gen_step',     action='store_true', help='generate toys')
argparser.add_argument('--do_fit_step',     action='store_true', help='fit toys')
argparser.add_argument('--do_pull_step',    action='store_true', help='draw pull distributions')
argparser.add_argument('--Ntoys',           type=int, default=10000, help='number of toys to generate')
argparser.add_argument('--Nfit',            type=int, default=10000, help='number of toys to fit')
argparser.add_argument('--r_gen_list',      type=float,  action='append', help='signal strength to generate toys')
argparser.add_argument('--gen_func_list',   type=str,  action='append', help='list of bkg functions to generate toys')
argparser.add_argument('--fit_func_list',   type=str,  action='append', help='list of bkg functions to fit toys')
argparser.add_argument('-y','--year',       type=str, default='22', help='year')
argparser.add_argument('-t','--tag',        type=str, default='',                                    help='tag for the output file')
argparser.add_argument('-c', '--category',  type=str, choices=['A', 'B', 'C', 'ABC'], default='ABC', help='categories')
args = argparser.parse_args()
print('\n')

dry_run         = args.dry_run

# parse argumemnts
Ntoys        = args.Ntoys
Nfit         = np.min([args.Nfit, Ntoys])
r_gen_list   = args.r_gen_list
gen_func_list= ['expo', 'const', 'poly1'] if not args.gen_func_list else args.gen_func_list
fit_func_list= gen_func_list if not args.fit_func_list else args.fit_func_list

year         = args.year
category_wp_dict = config.wp_dict[year]
categories = category_wp_dict.keys() if args.category == 'ABC' else [args.category]

mva_tag       = args.tag 
# loop on categories
for cat in categories:
    print(f'\n{ct.color_text.BOLD} --- CATEGORY {cat} --- {ct.color_text.END}')
    bdt_val      = f'{category_wp_dict[cat]:.4f}'
    tag          = f'WTau3Mu_{cat}{year}_{mva_tag}'

    if not r_gen_list:
        r_gen_list = [0.0, config.sensitivity_dict[year][cat], 3*config.sensitivity_dict[year][cat]]
    print(f'[i] GEN signal strength r = {r_gen_list}')

    # --- generate toys
    if args.do_gen_step:
        print(f'\n{ct.color_text.BOLD} --- GENERATION STEP --- {ct.color_text.END}')
        for gen_func in gen_func_list:
            gen_datacard = f'input_combine/datacard_WTau3Mu_{cat}{year}_{mva_tag}_{gen_func}_bdt{bdt_val}.root'
            if not os.path.isfile(gen_datacard):
                print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} datacard {gen_datacard} not found")
                if os.path.isfile(gen_datacard.replace('.root', '.txt')):
                    print(f"{ct.color_text.BOLD}[i]{ct.color_text.END}  compiling datacard {gen_datacard} with text2workspace.py")
                    cmd = f'text2workspace.py {gen_datacard.replace(".root", ".txt")} -o {gen_datacard} --X-assign-flatParam-prior'
                    if not dry_run : os.system(cmd)
                else : 
                    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} no datacard {gen_datacard} found")
                    exit(1)
            for r_gen in r_gen_list:
                print(f'\n{ct.color_text.BOLD} --- gen_func = {gen_func} \t r_gen = {r_gen:.1f} --- {ct.color_text.END}')
                cmd = f'python3 RunBiasMultiDimFit.py --mode generate --gen_func {gen_func} --input_datacard {gen_datacard} --nToys {Ntoys} --r_gen {r_gen:.1f} --tag {tag}'
                if not dry_run : os.system(cmd)
                else : print(cmd)

    # --- fit toys with different bkg functions and draw pull distributions
    if not args.do_fit_step and not args.do_pull_step: continue
    for r_gen in r_gen_list:
        print(f'\n{ct.color_text.BOLD} --- r_gen = {r_gen:.1f} --- {ct.color_text.END}')
        
        for fit_func in fit_func_list:
            fit_datacard = f'input_combine/datacard_WTau3Mu_{cat}{year}_{mva_tag}_{fit_func}_bdt{bdt_val}.root'
            for gen_func in gen_func_list:
                print(f'\n{ct.color_text.BOLD} --- gen_func = {gen_func} \t fit_func = {fit_func} --- {ct.color_text.END}')
                
                # fit
                if args.do_fit_step:
                    print(f'\n{ct.color_text.BOLD} --- FIT STEP --- {ct.color_text.END}')
                    cmd = f'python3 RunBiasMultiDimFit.py --mode fit_fixed --input_datacard {fit_datacard} --nToys {Ntoys} --nFit {Nfit} --r_gen {r_gen:.1f} --gen_func {gen_func} --fit_func {fit_func} --tag {tag}'
                    if not dry_run: os.system(cmd)
                    else : print(cmd)
                if args.do_pull_step:
                    print(f'\n{ct.color_text.BOLD} --- PULL STEP --- {ct.color_text.END}')
                    
                    cmd = f'python3 plot_bias_pull.py --gen_func {gen_func} --fit_func {fit_func} --nToys {Ntoys} --r_gen {r_gen:.1f} --tag {cat}{year}_{tag} --input_root {args.store_dir}/fit_results/higgsCombine.gen_{gen_func}_fit_{fit_func}_{tag}_r{r_gen:,.1f}.MultiDimFit.mH1.777_final.root --out_root fit_results/pull_results_gen_{gen_func}_fit_{fit_func}_{cat}{year}_{tag}_r{r_gen:,.1f}.root'
                    
                    if not dry_run: os.system(cmd)
                    else : print(cmd)