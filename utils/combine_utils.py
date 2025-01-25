import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import style.color_text as ct

import ROOT


latex_nuisances_names = {
    'Br_Vmux': '$Br(V\\to \\mu \\text{x})$',
    'Br_Vtaux': '$Br(V\\to \\tau \\text{x})$',
    'HLT_Tau3Mu_': 'HLT trimuon',
    'LxyS_cut': '\LxyS cut',
    'NLO':      'NLO re-weight', 
    'PU':    'PU re-weight',
    'lumi':         'luminosity', 
    'mc_stat': 'finite MC statistics', 
    'mu_mediumID': 'muon Medium ID',
    'pT_V':  'p$_T$($V$) mismodeling',
    'xsec_ppVx':  '$\sigma(pp \\to V+ \\text{x})$',
    'width_W': 'signal width W-ch',
    'width_Z': 'signal width Z-ch',
}

quantiles = {
    'nominal': 0.500,
    '1sigma': [0.160, 0.500, 0.840],
    'minus1sigma': 0.160,
    'plus1sigma': 0.840,
    '2sigma': [0.025, 0.500, 0.975],
    'minus2sigma': 0.025,
    'plus2sigma': 0.975,
    'all': [0.025, 0.160, 0.500, 0.840, 0.975],
}

#############################
#  ---- DATACARS UTILS ---- #
#############################

def fix_nuisances(datacard):
    with open(datacard, 'r') as f:
        lines = f.readlines()
    with open(datacard, 'w') as f:
        for line in lines:
            if 'kmax' in line: line = 'kmax * number of nuisance parameters\n'
            f.write(line)
    return 0

def combineCards_cmd(datacard_list, output, categories_list):
    
    # check categories and datacard_list have the same length
    if len(categories_list) != len(datacard_list):
        raise ValueError(f'{ct.color_text.RED} [ERROR] {ct.color_text.END} categories and datacard_list must have the same length')
        return None
    
    # remove .txt from datacard_list
    datacard_list = [datacard.split('.txt')[0] for datacard in datacard_list]
    
    cmd = f'combineCards.py '
    inputs = dict(zip(categories_list, datacard_list))
    for cat in inputs:
        cmd += f' {cat}={inputs[cat]}.txt'    
    cmd += f' > {output}.txt'
    
    return cmd

def compile_datacard(datacard, flat_prior = True, output_dir = None):
    
    if not os.path.isfile(datacard):
        raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} File {datacard} not found")
        return None
    if not output_dir:
        output = datacard.split('.txt')[0] + '.root'
    else:
        output = f'{output_dir}/{os.path.basename(datacard).split(".txt")[0]}.root'
    cmd = f'text2workspace.py {datacard} -o {output} ' + ('--X-assign-flatParam-prior' if flat_prior else '')
    os.system(cmd)
    
    # check if the output file exists
    if not os.path.isfile(output):
        raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} File {output} not found")
        return None
    else:
        print(f"{ct.color_text.GREEN}[+]{ct.color_text.END} Compiled datacard {datacard} into {output}")
        return output

def run_limit(datacard, out_name = 'no_tag', output_dir = None, method = 'AsymptoticLimits', CL = 0.90, quantileExpected = 0.500, n_toys = 10000, rMin = -10, rMax = 10):
        
        if not os.path.isfile(datacard):
            raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} File {datacard} not found")
            return None
        
        output_combine = f'higgsCombine{out_name}.{method}.mH120'
        
        cmd = f'combine -M {method} {datacard} -n {out_name} '
        if method == 'AsymptoticLimits':
            cmd += f' -t -1 '
            output_combine += '.root'
            
        elif method == 'HybridNew':
            cmd += f' --generateNuisances=1 --generateExternalMeasurements=0 --fitNuisances=1 --testStat LHC -T {n_toys}  --rule CLs --expectedFromGrid {quantileExpected} '

            output_combine += f'.quant{quantileExpected:.3f}.root'
        
        cmd += f' --cl {CL} --rMin {rMin} --rMax {rMax}'

        print(f"{ct.color_text.BOLD} execute {ct.color_text.END} {cmd}")
        os.system(cmd)
        # check if the output file exists
        if os.path.isfile(output_combine):
            os.system(f'mv {output_combine} {output_dir}')
            print(f"{ct.color_text.GREEN}[+]{ct.color_text.END} Limit computed and stored in {output_combine}")
        else:
            raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} output file {output_combine} not found")
        
        return 0

################################
#  ---- PLOTTING UTILS ---- #
################################

def plot_sb_model(workspace_file, 
                  output_dir = None,
                  tag = '',
                  n_bins = 65,
                  verbose = False
                  ):
    # output
    plot_path_name_base = f'{output_dir}/SB_PrePostFit' + (f'_{tag}' if tag else '')
    # inputs
    if os.path.isfile(workspace_file):
        print(f"{ct.color_text.GREEN}[+]{ct.color_text.END} Loading workspace from {workspace_file}")
        f = ROOT.TFile(workspace_file)
    else: raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} File {workspace_file} not found")
    
    w = f.Get("w")
    if not w: raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} Workspace not found in {workspace_file}")
    
    categories = w.cat("CMS_channel")
    if verbose:
        print(f"[+] Categories: ")
        [print(" - ", cat[0]) for cat in categories]

    binning = ROOT.RooFit.Binning(n_bins)
    data = w.data("data_obs")

    for cat in categories:
        print("... processing category ", cat[0])
        data_cat = data.reduce("CMS_channel==CMS_channel::"+cat[0])

        can = ROOT.TCanvas()
        plot = w.var("tau_fit_mass").frame()
        data_cat.plotOn(plot, binning)

        # Load the S+B model
        w.loadSnapshot("clean")
        sb_model = w.pdf("model_s").getPdf(cat[0])
        if not sb_model: raise ValueError(f"{ct.color_text.RED} [ERROR] {ct.color_text.END} signal model pre-fit not found")

        # Prefit
        #sb_model.plotOn( plot, ROOT.RooFit.LineColor(2), ROOT.RooFit.Name("prefit") )
        sb_model.plotOn( plot, 
                        ROOT.RooFit.LineColor(2),
                        ROOT.RooFit.Name("prefit"))

        # Postfit
        w.loadSnapshot("MultiDimFit")
        sb_model.plotOn( plot, 
                        ROOT.RooFit.LineColor(4), 
                        ROOT.RooFit.Name("postfit"))
        r_bestfit = w.var("r").getVal()

        plot.Draw()

        leg = ROOT.TLegend(0.15,0.75,0.45,0.90)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.04)
        leg.AddEntry("prefit", "Prefit S+B (r=1.00)", "L")
        leg.AddEntry("postfit", "Postfit S+B (r=%.2f)"%r_bestfit, "L")
        leg.Draw("Same")

        can.Update()
        can.SaveAs(f"{plot_path_name_base}_{cat[0]}.png")
        can.SaveAs(f"{plot_path_name_base}_{cat[0]}.pdf")
        can.Delete()
    print("r_bestfit = %.2f"%r_bestfit)

    return  0

################################
#  ---- PUBLICATION UTILS ---- #
################################

def systematics_Latex_table(datacard, output = None):

    Ncategories = 3

    with open(datacard, 'r') as f:
        lines = f.readlines()
    
    sys_name = []
    sys_type = []
    sys_values = []
    correlations = []
    for line in lines:
        if 'imax' in line or 'jmax' in line or 'kmax' in line: continue
        if 'lnN' in line or 'param' in line or 'rateParam' in line:
            syst = line.split()[0]
            kind = line.split()[1]
            values = [float(x) for x in line.split()[2:] if x.lstrip('-').replace('.', '', 1).isdigit()]
            # relative constraint for param
            if kind == 'param' :
                values = [values[1]/values[0]*100]
            else : values = [abs(x-1.)*100 for x in values]
            values = [f'{x:.2f}' for x in values]
            print(syst, values)
            if syst in latex_nuisances_names:
                sys_name.append(latex_nuisances_names[syst])
            else:
                sys_name.append(syst)
            sys_values.append(values)
            sys_type.append(kind)
    
    if output:
        with open(output, 'w') as f:
            f.write('\\begin{table}[h!]\n')
            f.write('\\centering\n')
            f.write('\\begin{tabular}{|c|c|}\n')
            f.write('\\hline\n')
            f.write('Systematic & Value \\\\ \n')
            f.write('\\hline\n')
            for syst in sys_name:
                f.write(f'{syst} & \\\\ \n')
            f.write('\\hline\n')
            f.write('\\end{tabular}\n')
            f.write('\\end{table}\n')
    else:
        print('\\begin{table}[h!]')
        print('\\centering')
        print('\\begin{tabular}{|c|c|}')
        print('\\hline')
        print('Systematic & Value \\\\ ')
        print('\\hline')
        for i, syst in enumerate(sys_name):
            print('\small{'+ syst + '}\t & sig &\t' + sys_type[i] + '&\t' + '&'.join(sys_values[i]) +' & - \\\\ ')
            #print(f'\'{syst}\': ')
        print('\\hline')
        print('\\end{tabular}')
        print('\\end{table}')
    return 0

def limit_Latex_table(directory, category = 'ABC', year = 22, combine_method = 'HybridNew'):

    return 0

# main
if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'results/AN_v5/input_combine/datacard_VTau3Mu_comb23_apply_LxyS2.0_pTVreweight_expo_bdt0.0000.txt'))
    systematics_Latex_table(path)
    