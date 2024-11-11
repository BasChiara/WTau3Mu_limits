import ROOT
import os
import utils
import sys
import numpy as np
sys.path.append('..')
import style.color_text as ct


def check_toy_dataset(toy_file, toy_name):
    f = ROOT.TFile(toy_file)
    if not f :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} file {toy_file} not found")
        exit(1)
    toy = f.Get(toy_name)
    if not toy :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} tree {toy_name} not found in {toy_file}")
        exit(1)
    return (toy.numEntries() > 0)

# --- argument pareser
args = (utils.get_arguments()).parse_args()
print('\n')

# --- setup
toy_tag          = f'.gen{args.nToys/1000:,.0f}K{args.gen_func}_{args.tag}_r{args.r_gen:,.1f}'
toys_file_name   = f'toys{toy_tag}'
tau_mass         = 1.777
do_single_fit    = False

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
    cmd = f'combine -M GenerateOnly -m {tau_mass} -d {args.input_datacard}  --setParameters Mtau={tau_mass} --freezeParameters Mtau --expectSignal {args.r_gen} -n {toy_tag}  --saveToys -t {args.nToys} -s -1\n\n'
    
    if not args.dry_run : os.system(cmd)
    else : print(cmd)
    
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
    
    limit_result = f'higgsCombine{fit_tag}.MultiDimFit.mH1.777'
    final_limit_result = f'fit_results/higgsCombine{fit_tag}.MultiDimFit.mH1.777_final.root'
    fit_result = f'multidimfit{fit_tag}.root'

    # set up the number of fits
    nFit             = args.nFit if args.nFit > 0 else args.nToys
    fit_to_do        = np.min([args.nToys, nFit])
    fit_done         = 0 

    if not do_single_fit :

        cmd = f'combine -M MultiDimFit {args.input_datacard} -m {tau_mass} --freezeParameters Mtau -t {args.nFit} -n {fit_tag} --expectSignal {args.r_gen} --toysFile {toys_file_name} --algo singles --rMin -50 --rMax 50 --trackParameters r -s 3872998\n\n'
        if not args.dry_run : os.system(cmd)
        else : print(cmd)
        # move fit result
        cmd = f'mv {limit_result}.3872998.root {final_limit_result}'
        if not args.dry_run : os.system(cmd)
        print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} fit result saved in {final_limit_result}')
        
    else :
        # remove all multi-dim fit results
        cmd = f'rm  {limit_result}* {fit_result}'
        if not args.dry_run : os.system(cmd)

        for i in range(fit_to_do) :
            print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} toy {i}')

            #check if dataset is empty
            if not check_toy_dataset(toys_file_name, f'toys/toy_{i+1}') :
                print(f"{ct.color_text.RED}[ALERT]{ct.color_text.END} toy {i+1} is empty --> skipping it")
                continue
            cmd = f'combine -M MultiDimFit {args.input_datacard} -m {tau_mass} --freezeParameters Mtau -n {fit_tag} --expectSignal {args.r_gen} -D {toys_file_name}:toys/toy_{i+1} --algo singles --rMin -20 --rMax 20 --saveFitResult \n\n'

            if args.dry_run : exit()
            os.system(cmd)

            # check if fit result exists
            if not os.path.isfile(fit_result) :
                print(f"{ct.color_text.RED}[ALERT]{ct.color_text.END} fit result {fit_result} not found --> something went wrong")
            else :
                file = ROOT.TFile(fit_result)
                res = file.Get('fit_mdf')
                status = res.status()
                print(f' - status = {status}')
                file.Close()
                # remove limit file if status is > 1 (fit invalid)
                #      check this issue https://root-forum.cern.ch/t/is-fit-validity-or-minimizer-status-more-important/30637
                if status > 1 :
                    print(f"{ct.color_text.RED}[ALERT]{ct.color_text.END} fit result {fit_result} is invalid --> removing it")
                    cmd = f'rm {limit_result}.root'
                    os.system(cmd)
                else :
                    # save fit result
                    cmd = f'mv {limit_result}.root fit_results/{limit_result}_toy{i+1}.root'
                    os.system(cmd)
                    print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} fit result saved in fit_results/{limit_result}_toy{i+1}.root')
                    fit_done += 1
        
        # hadd all fit results
        hadd_cmd = f'hadd -f -k -v 1 {final_limit_result} fit_results/{limit_result}_toy*.root'
        os.system(hadd_cmd)

        # remove all multi-dim fit results
        if os.path.isfile(final_limit_result) :
            cmd = f'rm fit_results/{limit_result}_toy*.root'
            os.system(cmd)
        print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} final fit result saved in {final_limit_result}')

    # print summary
    print(f'{ct.color_text.GREEN}[FIT]{ct.color_text.END} fits done {fit_done}/{fit_to_do}')
                