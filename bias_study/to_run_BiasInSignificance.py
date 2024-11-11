import os

to_generate = True 
to_fit = True
to_plot = True
debug = False 

general_tag="apply_LxyS2.0"

year_list=['22', '23']
cat_list=['A', 'B', 'C']
bdt_cuts_22 = [0.995, 0.996, 0.995]
bdt_cuts_23 = [0.987, 0.996, 0.992]

wp_dict = dict(zip(year_list, [dict(zip(cat_list, bdt_cuts_22)), dict(zip(cat_list, bdt_cuts_23))]))

func_list = ['expo', 'const', 'poly1'] 

# -- generation step --
if to_generate:
    for year in year_list:
        for cat in cat_list:
            bdt_cut = wp_dict[year][cat]
            if (debug and cat != 'A') or (debug and year != '22'): continue
            if (f'{cat}{year}' == 'A22'): continue
            for func in func_list:
                print(f'-- CAT {cat} 20{year} --\n generating {func}')
                tag = f'{cat}{year}_{general_tag}'
                gen_command = f'python3 AdaRunBiasInSignificance.py --input_datacard input_combine/datacard_WTau3Mu_{tag}_{func}_bdt{bdt_cut:.4f}.txt --tag {tag} --nToys 50000 --gen_func {func} --mode generate' 
                os.system(gen_command)
                
                print('\n')
# -- FIT STEP --

for year in year_list:
    for cat in cat_list:
        bdt_cut = wp_dict[year][cat]
        if (debug and cat != 'A') or (debug and year != '22'): continue
        if (f'{cat}{year}' == 'A22'): continue
        for gen_func in func_list:
            if to_fit:
                for fit_func in func_list:
                    print(f'-- CAT {cat} 20{year} --\n fitting {gen_func} with {fit_func}')
                    tag = f'{cat}{year}_{general_tag}'
                    fit_command = f'python3 AdaRunBiasInSignificance.py --input_datacard input_combine/datacard_WTau3Mu_{tag}_{fit_func}_bdt{bdt_cut:.4f}.txt --tag {tag} --nToys 50000 --gen_func {gen_func} --mode fixed --fit_func {fit_func}' 
                    os.system(fit_command)
                print('\n')
            if to_plot:
                # summary plot for each gen function
                print(f' -- Summary plot for {gen_func} --')
                summary_command = f'python3 AdaSummaryBiasSignificance.py --tag {tag} --gen_func {gen_func} --bdt_cut {bdt_cut:.4f} --use-mplhep'
                os.system(summary_command)
