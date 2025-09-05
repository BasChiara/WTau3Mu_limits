import ROOT
ROOT.gROOT.SetBatch(0)
import mplhep as hep
import itertools
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

import os
import glob
import numpy as np
import argparse

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from mva.config import LumiVal_plots 
import utils.combine_utils as Cutils

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_dir',                                                    default = 'binBDT_LxyS1.5_HLT_overlap_2024Apr29')
parser.add_argument('-d', '--datacard_tag',                                                 default = 'WTau3Mu_A22')
parser.add_argument('-o', '--plotout_dir',                                                  default = '/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/')
parser.add_argument('--scan_sensitivity',                                          )
parser.add_argument('-s', '--step',         choices = ['limit', 'merge', 'plot', 'all'],    default = 'all')
parser.add_argument('-n', '--name_combine',                                                 default = 'WTau3Mu_A22')
parser.add_argument('-M', '--method',       choices = ['AsymptoticLimits', 'HybridNew'],    default = 'AsymptoticLimits')
parser.add_argument('-y', '--year',                                                         default = '22')
#parser.add_argument('-c', '--category',     choices = ['AB', 'A', 'B', 'C'],                default = 'inclusive')
parser.add_argument('--CL',                 type =float,                                    default = 0.90)
parser.add_argument('-q', '--quantileExpected',type =float,                                 default = 0.500)
parser.add_argument('--stop_after',         type =int,                                      default = 1000)
parser.add_argument('--BDTmin',             type =float,                                    default = 0.990)
parser.add_argument('--BDTmax',             type =float,                                    default = 0.9995)
parser.add_argument('--BDTstep',            type =float,                                    default = 0.0005)

args = parser.parse_args()
debug = False

# define points BDT scan
bdt_cut_list = np.arange(args.BDTmin, args.BDTmax, args.BDTstep)
print(f'[*] BDT scan points: {len(bdt_cut_list)}')
# check directories with datacards
combine_dir = args.input_dir
if not os.path.isdir(combine_dir):
    print(f'[ERROR] cannot find directory {combine_dir}')
    exit(-1)
# global utils
datacard_tag = args.datacard_tag
datacard_name_base = '_'.join([
    f'{combine_dir}/datacard',
    datacard_tag, 
])

# make a list of datacards
print('\n---- COLLECT DATACARDS ----\n')
categories = ['A', 'B']
datacard_to_combine = {}
N = 1
for cat in categories:
    datacard_list = []
    for cut in bdt_cut_list:
        datacard_name = f'{combine_dir}/datacard_WTau3Mu_{cat}{args.year}_*{datacard_tag}*_bdt{cut:,.4f}'
        dtcs = glob.glob(datacard_name + '.txt')
        if len(dtcs) == 0:
            print(f'[INFO] no datacard found for {datacard_name}.txt')
            continue
        if len(dtcs) > 1:
            print(f'[ERROR] found more than one datacard for {datacard_name}.txt')
            exit(-1)
        datacard_list.append([[cat, cut], dtcs[0]])
    print(f'[*] CAT {cat}: found {len(datacard_list)} datacards')
    datacard_to_combine[cat] = datacard_list
    N *= len(datacard_list)

# print results 
for cat, datacards in datacard_to_combine.items():
    print(f' - {cat}:')
    for i, datacard in datacards:
        print(f'  - {i} : {os.path.basename(datacard)}')
print(f'[*] total number of combinations: {N}\n')

# combine and compile datacards
dtcs_set = list(itertools.product(*[datacard_to_combine[cat] for cat in categories])) # [ ( [[A, cut], datacard_A], [[B, cut], datacard_B] ), ... ]
datacard_compiled = []
working_points = []
for i, set in enumerate(dtcs_set):
    ncat = len(set)
    print(f'[*] combining datacards - {i+1}')

    dtcs = []
    wpoints = []
    for j, (cat_cut, datacard) in enumerate(set):
        print (f' - CAT {cat_cut[0]}: {datacard}')
        wpoints.append(cat_cut)
        dtcs.append(datacard)
    
    # -- compile
    this_tag = [f'{cat_cut[0]}' for cat_cut in wpoints]
    this_tag = ''.join(this_tag) if len(this_tag) > 1 else this_tag[0]
    this_dtc = f'{datacard_name_base}_cat{this_tag}_{i+1}'
    if os.path.exists(f'{this_dtc}.root'):
        print(f'[INFO] datacard {this_dtc}.root already exists, skip compilation')
        datacard_compiled.append(f'{this_dtc}.root')
        working_points.append(wpoints)
        continue
    
    cmd = Cutils.combineCards_cmd(dtcs, this_dtc, [f'cat{cat_cut[0]}' for cat_cut in wpoints])
    if not cmd:
        print(f'[ERROR] cannot create command to combine datacards')
        exit(-1)
    print(f' - {cmd}')
    os.system(cmd)
    if not os.path.exists(f'{this_dtc}.txt'):
        print(f'[ERROR] cannot find combined datacard {this_dtc}.txt')
        exit(-1)
    # -- compile datacard
    compiled_dtc = Cutils.compile_datacard(f'{this_dtc}.txt', flat_prior=False)
    if not os.path.exists(compiled_dtc):
        print(f'[ERROR] cannot find compiled datacard {compiled_dtc}')
        exit(-1)
    
    datacard_compiled.append(compiled_dtc)
    working_points.append(wpoints)
print(f'[*] compiled {len(datacard_compiled)} datacards')
print(f'[*] working points: {len(working_points)}')
print(working_points)

tree_name = 'limit'
merge_file = f'{args.input_dir}/Tau3MuCombine.{datacard_tag}_BDTscan.{args.method}.root'

# 1) compile datacards and calculate limit
if (args.step == 'all' or args.step == 'limit'):
    print('\n---- CALCULATE LIMITS ----')
    print(f'      with {args.method}\n')
    
    for i, datacard in enumerate(datacard_compiled):
        if( i+1 > args.stop_after): exit(-1)
        print(f'[*] processing {i+1}/{len(datacard_compiled)}: {datacard}')

        # calculate limits
        this_tag = [ f'{cat_cut[0]}' for cat_cut in working_points[i] ]
        this_tag = datacard_tag + (''.join(this_tag) if len(this_tag) > 1 else this_tag[0]) + f'{i+1}'
        if (args.method == 'AsymptoticLimits'):
            limit_cmd = f'combine -M {args.method} {datacard} -n .{this_tag} -t -1 --cl {args.CL}'
        elif (args.method == 'HybridNew'):
            limit_cmd = f'combine -M {args.method} {datacard} -n .{this_tag} --generateNuisances=1 --generateExternalMeasurements=0 --fitNuisances=1 --testStat LHC -T 10000 --rMin -10 --rMax 10 --rule CLs --expectedFromGrid {args.quantileExpected} --cl {args.CL}'
        #print(f' - {limit_cmd}')
        os.system(limit_cmd) 
        

# 2) collect and merge UL results
if (args.step == 'all' or args.step == 'merge'):    
    print('\n---- COLLECT RESULTS ----')
    tmp_files_list = []
    limit_value = []
    limit_err = []

    for i, datacard in enumerate(datacard_compiled):
        this_tag = [ f'{cat_cut[0]}' for cat_cut in working_points[i] ]
        this_tag = datacard_tag + (''.join(this_tag) if len(this_tag) > 1 else this_tag[0]) + f'{i+1}'
        combine_tag = f'{this_tag}.{args.method}.mH120' + ('.quant0.500' if args.method == 'HybridNew' else '')
        
        # crate a temporary .root -> attach scan point info to Combine output
        tmp_file = f'{args.input_dir}/tmp_{this_tag}.root'
        limit_rootfile_name = f'higgsCombine.{combine_tag}.root'
        if not os.path.exists(limit_rootfile_name):
            print(f'[INFO] could NOT find {limit_rootfile_name} --> skip this')
            continue
        limit_rdf   = ROOT.RDataFrame(tree_name, limit_rootfile_name).Define('index', f'{i}')
        limit_dict  = limit_rdf.AsNumpy()
        limit_rdf.Snapshot(tree_name, tmp_file)
        if os.path.exists(tmp_file):
            tmp_files_list.append(tmp_file) 
        else:
            print(f'[ERROR] cannot create snapshot {tmp_file}')
            exit(-1)
        if (args.method == 'AsymptoticLimits'):
            limit_value.append(limit_dict['limit'][2])
            limit_err.append(limit_dict['limitErr'][2])
        elif (args.method == 'HybridNew'):
            limit_value.append(limit_dict['limit'])
            limit_err.append(limit_dict['limitErr'])
    # merge combine output
    print('- now merge results')
    os.system(f'hadd -f {merge_file} ' + ' '.join([tmp_f for tmp_f in tmp_files_list]))
    if os.path.exists(merge_file):
        [os.system(f'rm {file}') for file in tmp_files_list]
        print(f'[INFO] removed tmp files')
    else :
        print(f'[ERROR] merge file {merge_file} NOT found')
        exit(-1)

# 3) show results
if (args.step == 'all' or args.step == 'plot'):
    print('\n---- PLOT LIMITS ----')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(True)
    import cmsstyle as CMS
    lumi = LumiVal_plots['20'+ args.year]
    CMS.SetLumi(f'20{args.year}, {lumi}')
    CMS.SetEnergy('13.6')
    #CMS.AppendAdditionalInfo(args.datacard_tag)
    
    #legend = CMS.cmsLeg(0.15, 0.70, 0.50, 0.90)
    # limit results
    results_rdf = ROOT.RDataFrame(tree_name, merge_file)
    results_np  = results_rdf.Filter('quantileExpected==0.5').AsNumpy()

    
    hist_2D = ROOT.TH2F('limit_2D', 'Expected Limit (r) for BDT cuts A and B', 
                        len(bdt_cut_list), bdt_cut_list[0] - args.BDTstep/2., bdt_cut_list[-1] + args.BDTstep/2. , 
                        len(bdt_cut_list), bdt_cut_list[0] - args.BDTstep/2., bdt_cut_list[-1] + args.BDTstep/2.)

    for i, idx in enumerate(results_np['index']):
        cut_A = working_points[idx][0][1]
        cut_B = working_points[idx][1][1]
        limit_value = results_np['limit'][i]
        hist_2D.Fill(cut_A, cut_B, limit_value)
    # plot results
    
    c = ROOT.TCanvas('c_limit', 'c_limit', 800, 600)
    c.SetRightMargin(0.15)
    c.SetLeftMargin(0.15)
    hist_2D.SetTitle(f'Expected Limit (r) for BDT cuts A and B')
    hist_2D.GetXaxis().SetTitle('BDT cut A')
    hist_2D.GetYaxis().SetTitle('BDT cut B')
    hist_2D.GetZaxis().SetTitle('Expected Limit (r)')
    hist_2D.Draw('COLZ text0')
    c.SaveAs(f'./Limit_BDTscan_{datacard_tag}_{args.method}.png')