import ROOT
import mplhep as hep
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

import os
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_dir',                                           default = 'binBDT_LxyS1.5_HLT_overlap_2024Apr29')
parser.add_argument('--scan_sensitivity',                                          )
parser.add_argument('-s', '--step',         choices = ['limit', 'merge', 'plot', 'all'],   default = 'all')
parser.add_argument('-d', '--datacard_tag',                                        default = 'WTau3Mu_A22')
parser.add_argument('-n', '--name_combine',                                        default = 'WTau3Mu_A22')
parser.add_argument('-M', '--method',       choices = ['AsymptoticLimits'],        default = 'AsymptoticLimits')
parser.add_argument('--CL',                 type =float,                           default = 0.90)
parser.add_argument('--BDTmin',             type =float,                           default = 0.990)
parser.add_argument('--BDTmax',             type =float,                           default = 0.9995)
parser.add_argument('--BDTstep',            type =float,                           default = 0.0005)

args = parser.parse_args()


bdt_cut_list = np.arange(args.BDTmin, args.BDTmax, args.BDTstep)
combine_dir = f'{args.input_dir}/'
if not os.path.isdir(combine_dir):
    print(f'[ERROR] cannot find directory {combine_dir}')
    exit(-1)
datacard_tag = args.datacard_tag

# 1) compile datacards and calculate limit
if (args.step == 'all' or args.step == 'limit'):
    print('* compile datacards and calculate limit *')
    for cut in bdt_cut_list:
        print(f' bdt > {cut:,.4f}')
        datacard_name = f'{combine_dir}/datacard_{datacard_tag}_bdt{cut:,.4f}'
        if not os.path.exists(f'{datacard_name}.txt') :
            print(f'[INFO] could NOT find {datacard_name}.txt --> skip this')
            bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
            continue
        os.system(f'text2workspace.py {datacard_name}.txt')
        if os.path.exists(f'{datacard_name}.root'):
            os.system(f'combine -M {args.method} {datacard_name}.root -n .{datacard_tag}_bdt{cut:,.4f}.{args.name_combine} -t -1 --cl {args.CL}') 
        else:
            print(f'[INFO] cannot find compiled datacard {datacard_name}.root')
            bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
            continue

# 2) collect and merge UL results
if (args.step == 'all' or args.step == 'merge'):
    # retrive sensitivity data
    if args.scan_sensitivity :
        print('* collect sensitivity results *')
        if not os.path.exists(args.scan_sensitivity):
            print(f'[ERROR] cannot find sensitivity file {args.scan_sensitivity}')
            exit(-1)
        sensitivity_np = (ROOT.RDataFrame('sensitivity_tree', args.scan_sensitivity)).AsNumpy()
        Punzi_S = sensitivity_np['PunziS_val'] 
        print(sensitivity_np['PunziS_val'])
    
    print('* collect combine results *')
    tree_name = 'limit'
    tmp_files_list = []
    limit_value = []
    limit_err = []
    for cut in bdt_cut_list:
        print(f' bdt > {cut:,.4f}')
        tmp_file = f'{args.input_dir}/tmp_{datacard_tag}_bdt{cut:,.4f}.root'
        limit_rootfile_name = f'higgsCombine.{datacard_tag}_bdt{cut:,.4f}.{args.name_combine}.AsymptoticLimits.mH120.root'
        if not os.path.exists(limit_rootfile_name):
            print(f'[INFO] could NOT find {limit_rootfile_name}.txt --> skip this')
            bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
            continue
        limit_rdf   = ROOT.RDataFrame(tree_name, limit_rootfile_name).Define('bdt_cut', f'{cut:,.4f}')
        limit_dict  = limit_rdf.AsNumpy()
        limit_rdf.Snapshot(tree_name, tmp_file)
        if os.path.exists(tmp_file):
            tmp_files_list.append(tmp_file) 
        else:
            print(f'[ERROR] cannot create snapshot {tmp_file}')
            exit(-1)
        limit_value.append(limit_dict['limit'][2])
        limit_err.append(limit_dict['limitErr'][2])
    print('- now merge results')
    merge_file = f'{args.input_dir}/Tau3MuCombine.{datacard_tag}_BDTscan.root'
    os.system(f'hadd -f {merge_file} {args.input_dir}/tmp_{datacard_tag}_bdt*.root')
    if os.path.exists(merge_file):
        [os.system(f'rm {file}') for file in tmp_files_list]
        print(f' removed tmp files')
    else :
        print(f'[ERROR] merge file {merge_file} NOT found')
        exit(-1)

    # 3) show results
if (args.step == 'all' or args.step == 'merge'):
     
    fig, ax1 = plt.subplots()
    hep.cms.label(
        label = "Preliminary", 
        data = True, 
        year = 2022,
        lumi = 34.7,
        com  = 13.6, 
        loc=2, 
        ax=ax1)
    ax2 = ax1.twinx()

    ax1.plot(bdt_cut_list, limit_value, 'bo--', linewidth=2, markersize=8, label =f'expUL ({args.CL*100}% CL)')
    ax2.plot(bdt_cut_list, Punzi_S,     'ro--', linewidth=2, markersize=8, label =f'Punzi sig.')
    ax1.set_ylabel(f'exp UL ({args.CL * 100} % CL)')
    ax2.set_ylabel(f'Punzi significance')
    ax1.set_xlabel('BDT threshold')
    ax1.set_xticks(np.arange(args.BDTmin, args.BDTmax, 4*args.BDTstep))
    fig.legend(loc='lower left', bbox_to_anchor =(0.15, 0.60))
    plt.savefig(f'{args.input_dir}/ULscan_{datacard_tag}.png')
    plt.savefig(f'{args.input_dir}/ULscan_{datacard_tag}.pdf')
