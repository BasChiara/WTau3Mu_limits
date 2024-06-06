import ROOT
import mplhep as hep
import matplotlib.pyplot as plt
plt.style.use([hep.style.ROOT, hep.style.firamath])

import os
import numpy as np
import argparse

# with combineCards.py and flat parameters : set kmax regardless of flat params
# - fix by manually setting kmax * in datacard
def fix_systematics(datacard_txt):
    # opne dtacard.txt
    with open(datacard_txt, 'r') as file:
        lines = file.readlines()
    new_lines = []
    for line in lines:
        # change manually the nuisance line
        if line.startswith('kmax'):
            words = line.split()
            words[1] = '*'
            new_line = ' '.join(words) +'\n'
        else: new_line = line
        new_lines.append(new_line)
    # write back the datacard
    with open(datacard_txt, 'w') as file:
        file.writelines(new_lines)
    print(f'[INFO] changed sys kmax in {datacard_txt}')

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_dir',                                           default = 'binBDT_LxyS1.5_HLT_overlap_2024Apr29')
parser.add_argument('--scan_sensitivity',                                          )
parser.add_argument('-s', '--step',         choices = ['limit', 'merge', 'plot', 'all'],   default = 'all')
parser.add_argument('-d', '--datacard_tag',                                        default = 'WTau3Mu')
parser.add_argument('-n', '--name_combine',                                        default = 'WTau3Mu')
parser.add_argument('-M', '--method',       choices = ['AsymptoticLimits', 'HybridNew'],        default = 'AsymptoticLimits')
parser.add_argument('--bdt_cut',            type =float,                           default = 0.990)
parser.add_argument('-y', '--year',                                                default = '22')
parser.add_argument('--CL',                 type =float,                           default = 0.90)
parser.add_argument('--stop_after',         type =int,                             default = 1000)
parser.add_argument('--BDTmin',             type =float,                           default = 0.990)
parser.add_argument('--BDTmax',             type =float,                           default = 0.9995)
parser.add_argument('--BDTstep',            type =float,                           default = 0.0005)

args = parser.parse_args()
debug = False
plot_dir = '/eos/user/c/cbasile/www/Tau3Mu_Run3/categorization/optimize_eta/'

# define points for the categorization scan
eta_points_AB = np.arange(0.5, 1.2, 0.1)
eta_points_BC = np.arange(1.5, 2.1, 0.1)
cat_points    = np.array(np.meshgrid(eta_points_AB, eta_points_BC)).T.reshape(-1, 2)
cat_name_id_dictionary = {'A':1, 'B':2, 'C':3}
# check directories with datacards
combine_dir = f'{args.input_dir}/'
if not os.path.isdir(combine_dir):
    print(f'[ERROR] cannot find directory {combine_dir}')
    exit(-1)
# global utils
datacard_name_base = '_'.join([
    f'{combine_dir}/datacard',
    args.datacard_tag,
    args.year,
    f'bdt{args.bdt_cut:,.4f}'
])
tree_name = 'limit'
merge_file = f'{args.input_dir}/Tau3MuCombine.{args.datacard_tag}_bdt{args.bdt_cut:,.4f}.{args.method}.CATscan.root'


# 1) combine & compile datacards -> calculate limit
if (args.step == 'all' or args.step == 'limit'):
    print('* combine & compile datacards + calculate limit *')
    
    for p, cat_p in enumerate(cat_points):
        if( p+1 > args.stop_after): exit(-1)
        #cat_p = cat_points[0]
        print(f'[*] eta AB = {cat_p[0]:,.1f} \t eta BC = {cat_p[1]:,.1f}')
        # id_tag for the current working point
        cat_p_tag          = f'etaAB{cat_p[0]:,.1f}_BC{cat_p[1]:,.1f}'
        datacard_name_list = [f'{datacard_name_base}_{cat}{args.year}_{cat_p_tag}' for cat in  cat_name_id_dictionary]
        cat_datacard_dict  = dict(zip(cat_name_id_dictionary.keys(), datacard_name_list))
        final_datacard_name= f'{datacard_name_base}_ABC{args.year}_{cat_p_tag}'
        
        # combine & compile
        combination_cmd    = f'combineCards.py '
        for cat in cat_datacard_dict:
            if not os.path.exists(f'{cat_datacard_dict[cat]}.txt') :
                print(f'[ERROR] could NOT find {cat_datacard_dict[cat]}.txt')
                exit(-1)
            else:
                combination_cmd += f'{args.datacard_tag}_{cat}{args.year}={cat_datacard_dict[cat]}.txt '
        combination_cmd += f'> {final_datacard_name}.txt'
        
        print(' - combine cards ')
        if(debug): print(combination_cmd)
        os.system(combination_cmd)
        if (args.method == 'HybridNew') : fix_systematics(f'{final_datacard_name}.txt')
        
        print(' - compile combined card ')
        os.system(f'text2workspace.py {final_datacard_name}.txt' + (' --X-assign-flatParam-prior' if args.method == 'HybridNew' else ''))

        # limit calculation
        combine_tag = f'{args.datacard_tag}_bdt{args.bdt_cut:,.4f}.{args.name_combine}_{cat_p_tag}'
        print(f' - calculate limit with {args.method}')
        if (args.method == 'AsymptoticLimits'):
            limit_cmd = f'combine -M {args.method} {final_datacard_name}.root -n .{combine_tag} -t -1 --cl {args.CL}'
        elif (args.method == 'HybridNew'):
            #limit_cmd = f'combine -M {args.method} {final_datacard_name}.root -n .{combine_tag} --generateNuisances=1 --generateExternalMeasurements=0 --fitNuisances=1 --testStat LHC -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.5 --cl {args.CL}'
            limit_cmd = f'combine -M {args.method} {final_datacard_name}.root -n .{combine_tag} --LHCmode LHC-limits -T 10000 --rMin 0 --rMax 10 --rule CLs --expectedFromGrid 0.5 --cl {args.CL}'

        if os.path.exists(f'{final_datacard_name}.root'):
            os.system(limit_cmd) 
        else:
            print(f'[ERROR] cannot find compiled datacard {final_datacard_name}.root')
            exit(-1)

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
    tmp_files_list = []
    limit_value = []
    limit_err = []
    
    for cat_p in cat_points:
    #cat_p = cat_points[0]
        print(f'[*] eta AB = {cat_p[0]:,.1f} \t eta BC = {cat_p[1]:,.1f}')
        cat_p_tag           = f'etaAB{cat_p[0]:,.1f}_BC{cat_p[1]:,.1f}'
        # create temporary root file
        combine_tag         = f'{args.datacard_tag}_bdt{args.bdt_cut:,.4f}.{args.name_combine}_{cat_p_tag}'
        tmp_file            = f'{args.input_dir}/tmp_{args.datacard_tag}_bdt{args.bdt_cut:,.4f}_{cat_p_tag}.root'
        # --> sistema sto schifo
        limit_rootfile_name = f'higgsCombine.{combine_tag}.{args.method}.mH120' + ('.quant0.500' if args.method == 'HybridNew' else '') +'.root'
        if not os.path.exists(limit_rootfile_name):
            print(f'[ERROR] could NOT find {limit_rootfile_name}.txt')
            exit(-1)
        # add branches
        limit_rdf   = ROOT.RDataFrame(tree_name, limit_rootfile_name).Define('bdt_cut', f'{args.bdt_cut:,.4f}').Define('eta_thAB', f'{cat_p[0]:,.1f}').Define('eta_thBC', f'{cat_p[1]:,.1f}')
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

    print('- now merge results')
    merge_cmd = f'hadd -f {merge_file} ' + ' '.join([tmp_f for tmp_f in tmp_files_list])
    os.system(merge_cmd)
    if os.path.exists(merge_file):
        [os.system(f'rm {tmp_f}') for tmp_f in tmp_files_list]
        print(f' removed tmp files')
    else :
        print(f'[ERROR] merge file {merge_file} NOT found')
        exit(-1)
   
# 3) show results
if (args.step == 'all' or args.step == 'plot'):
    ROOT.gStyle.SetOptStat(0)
    import cmsstyle as CMS
    CMS.SetLumi('2022, 34.4')
    CMS.SetEnergy('13.6')
    results_rdf = ROOT.RDataFrame(tree_name, merge_file)
    limit_map   = results_rdf.Filter('quantileExpected==0.5').Profile2D(
        ('limit_map', '', 
        len(eta_points_AB), eta_points_AB[0] - 0.05, eta_points_AB[-1] + 0.05, # x asxis
        len(eta_points_BC), eta_points_BC[0] - 0.05, eta_points_BC[-1] + 0.05, # y axis
        0, 10. 
        ),
        'eta_thAB', 'eta_thBC', 'limit').GetPtr()
    limit_map.GetZaxis().SetTitle("exp UL (90% CL)")
    limit_map.GetZaxis().SetTitleOffset(1.35)
    limit_map.GetZaxis().SetTitleSize(0.035)
    limit_map.GetZaxis().SetLabelSize(0.035)
    limit_map.GetZaxis().SetLabelOffset(0.005)
     
    c = CMS.cmsCanvas(
        'c',
        eta_points_AB[0]  - 0.05 ,
        eta_points_AB[-1] + 0.05,
        eta_points_BC[0]  - 0.05,
        eta_points_BC[-1] + 0.05,
        "|#eta|_{AB} threshold","|#eta|_{BC} threshold",
        square=CMS.kSquare,extraSpace=0.03,iPos=0.0,with_z_axis=True,scaleLumi=0.80)
    #c = ROOT.TCanvas('c', 'c', 800, 800)
    c.cd()
    CMS.SetCMSPalette()
    limit_map.SetMarkerColor(ROOT.kWhite)
    ROOT.gStyle.SetPaintTextFormat("1.3f")
    #limit_map.cmsDraw("colz text")
    CMS.cmsDraw(limit_map, 
        'colz text',
        marker = limit_map.GetMarkerStyle(),
        mcolor = limit_map.GetMarkerColor(), 
        fcolor = limit_map.GetFillColor(),
        fstyle = limit_map.GetFillStyle(), 
    )
    
    c.SaveAs(f'{plot_dir}/ULscan_categories_{args.method}_bdt{args.bdt_cut:,.4f}_{args.datacard_tag}.png')
    c.SaveAs(f'{plot_dir}/ULscan_categories_{args.method}_bdt{args.bdt_cut:,.4f}_{args.datacard_tag}.pdf')
    #hep.cms.label(
    #    label = "Preliminary",
    #    data = True, 
    #    year = 2022,
    #    lumi = 34.7,
    #    com  = 13.6, 
    #    loc=2, 
    #    ax=ax1)
    ##ax2 = ax1.twinx()
    ##limit_value = np.array(limit_value, dtype=float).reshape(-1,2)
    #ax1.contour(eta_points_AB[0], eta_points_BC[0], limit_value, label =f'expUL ({args.CL*100}% CL)')
    ##ax2.contour(cat_points, Punzi_S,     'ro--', linewidth=2, markersize=8, label =f'Punzi sig.')
    ##ax1.set_ylabel(f'exp UL ({args.CL * 100} % CL)')
    ##ax2.set_ylabel(f'Punzi significance')
    ##ax1.set_xlabel('BDT threshold')
    ##ax1.set_xticks(np.arange(args.BDTmin, args.BDTmax, 4*args.BDTstep))
    #fig.legend(loc='lower left', bbox_to_anchor =(0.15, 0.60))
    #plt.savefig(f'{args.input_dir}/ULscan_categories_{datacard_tag}.png')
    #plt.savefig(f'{args.input_dir}/ULscan_categories_{datacard_tag}.pdf')
