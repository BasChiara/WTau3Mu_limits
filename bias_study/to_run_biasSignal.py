import utils
import os
import sys
sys.path.append('..')
import style.color_text as ct

dry_run = False
do_gen_step     = False
do_fit_step     = False
do_pull_step    = True

# signal strength to generate toys
Ntoys        = 50000
r_gen_list   = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 10.0]
r_gen_list   = [0.5, 1.0] 
gen_func     = 'expo'
fit_func_list= ['expo', 'const']

category_list = ['A22', 'B22', 'C22']
#category_list = ['C22']
bdt_cut_list  = ['0.9940', '0.9970', '0.9930']
#bdt_cut_list  = ['0.9930']
category_wp_dict = dict(zip(category_list, bdt_cut_list))
mva_tag       = 'LxyS2.1_2024Jul11' 
# loop on categories
for cat in category_list:
    print(f'\n{ct.color_text.BOLD} --- CATEGORY {cat} --- {ct.color_text.END}')
    tag          = f'WTau3Mu_{cat}_{mva_tag}_bdt{category_wp_dict[cat]}'
    gen_datacard = f'input_combine/datacard_WTau3Mu_{cat}_{mva_tag}_{gen_func}_bdt{category_wp_dict[cat]}.root'

    # --- generate toys
    if do_gen_step:
        print(f'\n{ct.color_text.BOLD} --- GENERATION STEP --- {ct.color_text.END}')
        for r_gen in r_gen_list:
            cmd = f'python3 RunBiasMultiDimFit.py --mode generate --input_datacard {gen_datacard} --nToys {Ntoys} --r_gen {r_gen} --tag {tag}'
            if not dry_run : os.system(cmd)
            else : print(cmd)

    # --- fit toys with different bkg functions and draw pull distributions
    for r_gen in r_gen_list:
        print(f'\n{ct.color_text.BOLD} --- r_gen = {r_gen} --- {ct.color_text.END}')
        for fit_func in fit_func_list:
            print(f'\n{ct.color_text.BOLD} --- gen_func = {gen_func} \t fit_func = {fit_func} --- {ct.color_text.END}')
            
            fit_datacard = f'input_combine/datacard_WTau3Mu_{cat}_{mva_tag}_{fit_func}_bdt{category_wp_dict[cat]}.root'
            # fit
            if do_fit_step:
                print(f'\n{ct.color_text.BOLD} --- FIT STEP --- {ct.color_text.END}')
                cmd = f'python3 RunBiasMultiDimFit.py --mode fit_fixed --input_datacard {fit_datacard} --nToys {Ntoys} --r_gen {r_gen} --gen_func {gen_func} --fit_func {fit_func} --tag {tag}'
            
                if not dry_run: os.system(cmd)
                else : print(cmd)
            if do_pull_step:
                print(f'\n{ct.color_text.BOLD} --- PULL STEP --- {ct.color_text.END}')
                
                cmd = f'python3 plot_bias_pull.py --gen_func {gen_func} --fit_func {fit_func} --nToys {Ntoys} --r_gen {r_gen} --tag {tag} --input_root higgsCombine.gen_{gen_func}_fit_{fit_func}_{tag}_r{r_gen:,.1f}.MultiDimFit.mH1.777.123456.root --out_root pull_results_gen_{gen_func}_fit_{fit_func}_{tag}_r{r_gen:,.1f}.root'
                
                if not dry_run: os.system(cmd)
                else : print(cmd)