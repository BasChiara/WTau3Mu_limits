import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import style.color_text as ct


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


# main
if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'results/AN_v5/input_combine/datacard_VTau3Mu_comb23_apply_LxyS2.0_pTVreweight_expo_bdt0.0000.txt'))
    systematics_Latex_table(path)
    