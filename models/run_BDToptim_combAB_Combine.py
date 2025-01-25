import ROOT
ROOT.gROOT.SetBatch(0)
import mplhep as hep
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
parser.add_argument('-o', '--plotout_dir',                                                  default = '/eos/user/c/cbasile/www/Tau3Mu_Run3/BDTtraining/cut_LxySign/')
parser.add_argument('--scan_sensitivity',                                          )
parser.add_argument('-s', '--step',         choices = ['limit', 'merge', 'plot', 'all'],    default = 'all')
parser.add_argument('-d', '--datacard_tag',                                                 default = 'WTau3Mu_A22')
parser.add_argument('-n', '--name_combine',                                                 default = 'WTau3Mu_A22')
parser.add_argument('-M', '--method',       choices = ['AsymptoticLimits', 'HybridNew'],    default = 'AsymptoticLimits')
parser.add_argument('-y', '--year',                                                         default = '22')
parser.add_argument('-c', '--category',     choices = ['AB', 'A', 'B', 'C'],                default = 'inclusive')
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
# check directories with datacards
combine_dir = f'{args.input_dir}/'
if not os.path.isdir(combine_dir):
    print(f'[ERROR] cannot find directory {combine_dir}')
    exit(-1)
# global utils
datacard_tag = args.datacard_tag
datacard_name_base = '_'.join([
    f'{combine_dir}/datacard',
    datacard_tag, 
])

print(f'[*] datacard tag: {datacard_tag}')
exit()
# make a list of datacards
datacard_list = []
for cut in bdt_cut_list:
    datacard_name = f'{datacard_name_base}_bdt{cut:,.4f}'
    if not os.path.exists(f'{datacard_name}.txt') :
        print(f'[INFO] cannot find {datacard_name}.txt --> skip this')
        bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
        continue
    datacard_list.append(datacard_name)



tree_name = 'limit'
merge_file = f'{args.input_dir}/Tau3MuCombine.{datacard_tag}_BDTscan.{args.method}.root'

# 1) compile datacards and calculate limit
if (args.step == 'all' or args.step == 'limit'):
    print('* compile datacards and calculate limit *')
    
    for i, cut in enumerate(bdt_cut_list):
        if( i+1 > args.stop_after): exit(-1)
        print(f'[*] BDT > {cut:,.4f}')
        
        # check datacard
        datacard_name = f'{datacard_name_base}_bdt{cut:,.4f}'
        if not os.path.exists(f'{datacard_name}.txt') :
            print(f'[INFO] cannot find {datacard_name}.txt --> skip this')
            bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
            continue

        Cutils.fix_nuisances(datacard_name+'.txt')
        
        # compile
        print(' - compile datacard ')
        os.system(f'text2workspace.py {datacard_name}.txt --X-assign-flatParam-prior' )
        if not os.path.exists(f'{datacard_name}.root'):
            print(f'[INFO] cannot find compiled datacard {datacard_name}.root --> skip this')
            bdt_cut_list = np.delete(bdt_cut_list,np.argwhere(bdt_cut_list==cut))
            continue
        
        # calculate limits
        print(f' - calculate limit with {args.method}')
        combine_tag = f'{datacard_tag}_bdt{cut:,.4f}' + (f'.{args.name_combine}' if args.name_combine != args.datacard_tag else '')
        if (args.method == 'AsymptoticLimits'):
            limit_cmd = f'combine -M {args.method} {datacard_name}.root -n .{combine_tag} -t -1 --cl {args.CL}'
        elif (args.method == 'HybridNew'):
            limit_cmd = f'combine -M {args.method} {datacard_name}.root -n .{combine_tag} --generateNuisances=1 --generateExternalMeasurements=0 --fitNuisances=1 --testStat LHC -T 10000 --rMin -10 --rMax 10 --rule CLs --expectedFromGrid {args.quantileExpected} --cl {args.CL}'
            #limit_cmd = f'combine -M {args.method} {datacard_name}.root -n .{combine_tag} --LHCmode LHC-limits -T 10000 --rMin -10 --rMax 10 --rule CLs --expectedFromGrid {args.quantileExpected} --cl {args.CL}'
        print(f' - {limit_cmd}')
        os.system(limit_cmd) 
        

# 2) collect and merge UL results
if (args.step == 'all' or args.step == 'merge'):    
    print('* collect combine results *')
    tmp_files_list = []
    limit_value = []
    limit_err = []

    for cut in bdt_cut_list:
        print(f'[*] BDT > {cut:,.4f}')
        bdt_p_tag   = f'{datacard_tag}_bdt{cut:,.4f}' + (f'.{args.name_combine}' if args.name_combine != args.datacard_tag else '')
        combine_tag = f'{bdt_p_tag}.{args.method}.mH120' + ('.quant0.500' if args.method == 'HybridNew' else '')
        
        # crate a temporary .root -> attach scan point info to Combine output
        tmp_file = f'{args.input_dir}/tmp_{bdt_p_tag}.root'
        limit_rootfile_name = f'higgsCombine.{combine_tag}.root'
        if not os.path.exists(limit_rootfile_name):
            print(f'[INFO] could NOT find {limit_rootfile_name} --> skip this')
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
    ROOT.gStyle.SetOptStat(0)
    import cmsstyle as CMS
    lumi = LumiVal_plots['20'+ args.year]
    CMS.SetLumi(f'2022, {lumi}')
    CMS.SetEnergy('13.6')
    CMS.AppendAdditionalInfo(args.datacard_tag)
    
    legend = CMS.cmsLeg(0.15, 0.70, 0.50, 0.90)
    # limit results
    results_rdf = ROOT.RDataFrame(tree_name, merge_file)
    results_np  = results_rdf.Filter('quantileExpected==0.5').AsNumpy()
    limit_graph = results_rdf.Filter(f'quantileExpected==0.5 & bdt_cut > {bdt_cut_list[0]} & (bdt_cut < ({bdt_cut_list[-1]} + {args.BDTstep/2.}) )').Graph('bdt_cut', 'limit').GetPtr()
    limit_graph.SetMarkerColor(ROOT.kBlue)
    limit_graph.SetMarkerStyle(20)
    limit_graph.SetLineColor(ROOT.kBlue)
    limit_graph.SetMarkerSize(1.5)
    legend.AddEntry(limit_graph, f'{args.method}')
    c = CMS.cmsCanvas(
        'c',
        bdt_cut_list[0] - 0.0005,
        1.0,
        0.8*np.min(results_np['limit']),
        1.2*np.max(results_np['limit']),
        'BDTcut',f'expUL ({args.CL*100} %)',
        square=CMS.kRectangular,extraSpace=0.01,iPos=0.0,scaleLumi=0.80
    )
    c.cd()
    CMS.cmsDraw(limit_graph, 
        'LP',
        marker = limit_graph.GetMarkerStyle(),
        mcolor = limit_graph.GetMarkerColor(), 
        fcolor = limit_graph.GetFillColor(),
        fstyle = limit_graph.GetFillStyle(), 
    )
    legend.Draw()
    
    CMS.cmsGrid(True)
    c.SaveAs(f'{args.plotout_dir}/ULscan_BDT_{args.method}_{args.datacard_tag}.png')
    c.SaveAs(f'{args.plotout_dir}/ULscan_BDT_{args.method}_{args.datacard_tag}.pdf')

    # retrive sensitivity data
    if args.scan_sensitivity :
        print('* collect sensitivity results *')
        if not os.path.exists(args.scan_sensitivity):
            print(f'[ERROR] cannot find sensitivity file {args.scan_sensitivity}')
            exit(-1)
        sensitivity_rdf =  ROOT.RDataFrame('sensitivity_tree', args.scan_sensitivity)
        sensitivity_np  = (ROOT.RDataFrame('sensitivity_tree', args.scan_sensitivity)).AsNumpy()

        fig, ax1 = plt.subplots(figsize = (12,8))
        hep.cms.label(
            label = "Preliminary", 
            data = True, 
            year = '20' + args.year,
            lumi = LumiVal_plots['20'+ args.year],
            com  = 13.6, 
            loc=0, 
            ax=ax1
        )
        ax2 = ax1.twinx()

        #print(results_np['bdt_cut'].isin(bdt_cut_list))
        #exit()
        #ax1.plot(bdt_cut_list[:len(results_np['limit'])], results_np['limit'],              'bo--', linewidth=2, markersize=8, label =f'expUL ({args.CL*100}% CL)')
        ax1.errorbar(bdt_cut_list[:len(results_np['limit'])], results_np['limit'], yerr = results_np['limitErr'], fmt='bo--', linewidth=2, markersize=8, label =f'expUL')
        ax2.errorbar(sensitivity_np['bdt_cut'], sensitivity_np['PunziS_val'], yerr = sensitivity_np['PunziS_err'], fmt='ro--', linewidth=2, markersize=8, label =f'Punzi signifince')
        ax1.set_ylim(0.8*np.min(results_np['limit']), 1.2*np.max(results_np['limit']))
        ax2.set_ylim(0.05, 0.25 if not args.category == 'C' else 0.20)
        # add text with process info
        #ax2.plot(sensitivity_np['bdt_cut'], sensitivity_np['PunziS_val'],     'ro--', linewidth=2, markersize=8, label =f'Punzi sig.')
        ax1.set_ylabel(f'exp UL ({args.CL * 100} % CL) '+ r'$\times 10^{-7}$')
        ax2.set_ylabel(f'Punzi significance')
        ax1.set_xlabel('BDT threshold')
        ax1.set_xticks(np.arange(args.BDTmin, args.BDTmax, 2*args.BDTstep))
        ax1.grid(True)
        fig.legend(loc='lower left', bbox_to_anchor =(0.15, 0.70))
        plt.savefig(f'{args.plotout_dir}/ULvsPUNZIscan_BDT_{args.method}_{args.datacard_tag}.png')
        plt.savefig(f'{args.plotout_dir}/ULvsPUNZIscan_BDT_{args.method}_{args.datacard_tag}.pdf')
        print(f'[INFO] plot saved in {args.plotout_dir}/ULvsPUNZIscan_BDT_{args.method}_{args.datacard_tag}.png/pdf')
