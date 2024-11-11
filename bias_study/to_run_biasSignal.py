import utils
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import style.color_text as ct
import mva.config as config

dry_run = False
do_gen_step     = False
do_fit_step     = True
do_pull_step    = True

# signal strength to generate toys
Ntoys        = 10000
r_gen_list   = [0.0, 1.5, 5.0]
r_gen_list   = [0.0]
year         = '22'    
gen_func_list= ['expo']#['expo', 'const']
fit_func_list= ['expo']#['expo', 'const']


category_wp_dict = config.wp_dict[year]
categories = category_wp_dict.keys()
categories = ['A']
mva_tag       = 'apply_LxyS2.0'
# loop on categories
for cat in categories:
    print(f'\n{ct.color_text.BOLD} --- CATEGORY {cat} --- {ct.color_text.END}')
    bdt_val      = f'{category_wp_dict[cat]:.4f}'
    tag          = f'WTau3Mu_{cat}{year}_{mva_tag}_bdt{category_wp_dict[cat]}'

    
    # --- generate toys
    if do_gen_step:
        print(f'\n{ct.color_text.BOLD} --- GENERATION STEP --- {ct.color_text.END}')
        for gen_func in gen_func_list:
            gen_datacard = f'input_combine/datacard_WTau3Mu_{cat}{year}_{mva_tag}_{gen_func}_bdt{bdt_val}.root'
            for r_gen in r_gen_list:
                print(f'\n{ct.color_text.BOLD} --- gen_func = {gen_func} \t r_gen = {r_gen} --- {ct.color_text.END}')
                cmd = f'python3 RunBiasMultiDimFit.py --mode generate --gen_func {gen_func} --input_datacard {gen_datacard} --nToys {Ntoys} --r_gen {r_gen} --tag {tag}'
                if not dry_run : os.system(cmd)
                else : print(cmd)

    # --- fit toys with different bkg functions and draw pull distributions
    for r_gen in r_gen_list:
        print(f'\n{ct.color_text.BOLD} --- r_gen = {r_gen} --- {ct.color_text.END}')
        
        for fit_func in fit_func_list:
            fit_datacard = f'input_combine/datacard_WTau3Mu_{cat}{year}_{mva_tag}_{fit_func}_bdt{bdt_val}.root'
            for gen_func in gen_func_list:
                print(f'\n{ct.color_text.BOLD} --- gen_func = {gen_func} \t fit_func = {fit_func} --- {ct.color_text.END}')
                
                # fit
                if do_fit_step:
                    print(f'\n{ct.color_text.BOLD} --- FIT STEP --- {ct.color_text.END}')
                    cmd = f'python3 RunBiasMultiDimFit.py --mode fit_fixed --input_datacard {fit_datacard} --nToys {Ntoys} --r_gen {r_gen} --gen_func {gen_func} --fit_func {fit_func} --tag {tag}'
                
                    if not dry_run: os.system(cmd)
                    else : print(cmd)
                if do_pull_step:
                    print(f'\n{ct.color_text.BOLD} --- PULL STEP --- {ct.color_text.END}')
                    
                    cmd = f'python3 plot_bias_pull.py --gen_func {gen_func} --fit_func {fit_func} --nToys {Ntoys} --r_gen {r_gen} --tag {cat}{year}_{tag} --input_root higgsCombine.gen_{gen_func}_fit_{fit_func}_{tag}_r{r_gen:,.1f}.MultiDimFit.mH1.777.123456.root --out_root pull_results_gen_{gen_func}_fit_{fit_func}_{cat}{year}_{tag}_r{r_gen:,.1f}.root'
                    
                    if not dry_run: os.system(cmd)
                    else : print(cmd)