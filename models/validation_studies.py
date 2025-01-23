import ROOT

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import utils.combine_utils as utils
import style.color_text as ct

import argparse

def argumenst_parser():
    parser = argparse.ArgumentParser(description='Several statistical validation studies')
    parser.add_argument('--workdir',    help='Directory with the datacards')
    parser.add_argument('--datacard',   help='Datacard to be used')
    parser.add_argument('--tag',        help='Identifier for the datacard')
    parser.add_argument('--category',   help='Category to be used')
    parser.add_argument('--output',     help='Output file')
    parser.add_argument('--dry_run', action='store_true',   help='Verbosity level')
    # NLL scan
    parser.add_argument('--NLLscan_points',       default=50,    help='Number of points for the NLL scan')
    parser.add_argument('--NLLscan_rlo',          default=-0.5,  help='min r for the NLL scan')
    parser.add_argument('--NLLscan_rhi',          default=1.5,   help='MAX r for the NLL scan')
    parser.add_argument('--NLLscan_breakdown',    action='store_true', help='Breakdown of systematics uncertainties')

    return parser.parse_args()

def go_combine_cmd(command, dry_run, output):

    if not output.endswith('.root'): raise ValueError(f'{ct.color_text.RED} [ERROR] {ct.color_text.END} in {output} :\n   --> output must be a .root file')
    combine_out = os.path.basename(output)
    if dry_run:
        print(f'[DRY-RUN] {command}')
    else:
        os.system(command)
        os.system(f'mv {combine_out} {output}')
        print(f' > {combine_out} saved in {workdir}/combine_output')
    return 0


args = argumenst_parser()
workdir = args.workdir
# setup output directory for combine root files
if not os.path.isdir(workdir+'/combine_output'):
    os.mkdir(workdir+'/combine_output')
    print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} created directory {workdir}/combine_output')
else:
    print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} directory {workdir}/combine_output already exists')
# setup output directory for plots
if not os.path.isdir(workdir+'/plots'):
    os.mkdir(workdir+'/plots')
    print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} created directory {workdir}/plots')
else:
    print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} directory {workdir}/plots already exists')

tag = args.tag
output = args.output

# --- S+B model pre and post fit
print('\n')
print(f'{ct.color_text.BOLD}----- SIGNAL + BACKGROUND PRE POST FIT ----- {ct.color_text.END}')

job_tag = f'.{tag}_bestfit'
combine_cmd = f'combine -M MultiDimFit {args.datacard} --saveWorkspace -n {job_tag}'
combine_out_bestfit = f'higgsCombine{job_tag}.MultiDimFit.mH120.root'
go_combine_cmd(
    command=combine_cmd, 
    dry_run=args.dry_run, 
    output=f'{workdir}/combine_output/{combine_out_bestfit}'
)

utils.plot_sb_model(f'{workdir}/combine_output/{combine_out_bestfit}', tag = tag, output_dir = f'{workdir}/plots/', verbose = True)


# --- Likelyhood scan
print('\n')
print(f'{ct.color_text.BOLD}----- LIKELYHOOD SCAN ----- {ct.color_text.END}')

# sys + stat
job_tag = f'.{tag}_NLLscan'
combine_cmd = f'combine -M MultiDimFit {args.datacard} --algo grid --points {args.NLLscan_points} --setParameterRanges r={args.NLLscan_rlo},{args.NLLscan_rhi} -n {job_tag}'
combine_out = f'higgsCombine{job_tag}.MultiDimFit.mH120.root'
go_combine_cmd(
    command=combine_cmd, 
    dry_run=args.dry_run, 
    output=f'{workdir}/combine_output/{combine_out}'
)
if not args.NLLscan_breakdown:
    job_tag = job_tag.replace('.','')
    plot_cmd = f'plot1DScan.py {workdir}/combine_output/{combine_out} -o {workdir}/plots/{job_tag}'
    os.system(plot_cmd)
else:
    # stat only
    job_tag_stat = f'.{tag}_NLLscan_statOnly'
    
    combine_out_stat = f'higgsCombine{job_tag_stat}.MultiDimFit.mH120.root'
    combine_out_sys = f'{workdir}/combine_output/{combine_out}'
    combine_out_bestfit = f'{workdir}/combine_output/{combine_out_bestfit}'
    
    # ! systematics are fixed to their best fit values
    combine_cmd = f'combine -M MultiDimFit {combine_out_bestfit} --algo grid --points {args.NLLscan_points} --setParameterRanges r={args.NLLscan_rlo},{args.NLLscan_rhi} -n {job_tag_stat} --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'
    go_combine_cmd(
        command=combine_cmd, 
        dry_run=args.dry_run, 
        output=f'{workdir}/combine_output/{combine_out_stat}'
        )

    job_tag = job_tag.replace('.','')
    plot_cmd = f'plot1DScan.py {combine_out_sys} --main-label "sys + stat" --main-color 1 --others {workdir}/combine_output/{combine_out_stat}:"stat only":2 -o {workdir}/plots/{job_tag} --breakdown syst,stat'
    os.system(plot_cmd)

# --- Impacts
print('\n')
print(f'{ct.color_text.BOLD}----- IMPACTS ----- {ct.color_text.END}')

job_tag = f'impacts.{tag}'
sys_json = f'{workdir}/combine_output/impacts_{tag}.json'
# POI fit
combine_cmd = f'combineTool.py -M Impacts -d {args.datacard} -m 1.78 -n {job_tag} --setParameterRanges r={args.NLLscan_rlo},{args.NLLscan_rhi} --doInitialFit --robustFit 1'
os.system(combine_cmd)
# Nuisance fit
combine_cmd = f'combineTool.py -M Impacts -d {args.datacard} -m 1.78 -n {job_tag} --setParameterRanges r={args.NLLscan_rlo},{args.NLLscan_rhi} --doFits --robustFit 1'
os.system(combine_cmd)
# Collect results
combine_cmd = f'combineTool.py -M Impacts -d {args.datacard} -m 1.78 -n {job_tag} --setParameterRanges r={args.NLLscan_rlo},{args.NLLscan_rhi} -o {sys_json}'
os.system(combine_cmd)
move_cmd = f'mv higgsCombine_*Fit_{job_tag}*.mH1.78.root {workdir}/combine_output/'
os.system(move_cmd)
print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} impacts saved in {sys_json}')

# plot impacts
plot_cmd = f'plotImpacts.py -i {sys_json} -o {workdir}/plots/impacts_{tag}'
os.system(plot_cmd)
print(f'{ct.color_text.BOLD}[+]{ct.color_text.END} impacts plot saved in {workdir}/plots/impacts_{tag}.pdf')

# --- 