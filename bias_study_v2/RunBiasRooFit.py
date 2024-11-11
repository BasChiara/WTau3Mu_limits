import ROOT
ROOT.gROOT.SetBatch(True)
import os
import utils
import sys
import numpy as np
sys.path.append('..')
import style.color_text as ct
import mva.config as config

# --- argument pareser
parser = utils.get_arguments()
parser.add_argument('-c','--category', choices=['A', 'B', 'C'], default='A', help='category to fit')
parser.add_argument('-y','--year',   default='22', help='year of data taking')
args = parser.parse_args()

print('\n')

# --- setup
category_tag     = f'{args.category}{args.year}'
toy_tag          = f'.gen{args.nToys/1000:,.0f}K{args.gen_func}_WTau3Mu_{args.category}{args.year}_{args.tag}' + (f'_r{args.r_gen:,.1f}' if args.r_gen > -1 else '')
toys_file_name   = f'toys{toy_tag}.root'
tau_mass     = 1.777
Ntoy_to_process = args.nToys if args.nFit > args.nToys else args.nFit

out_plot_file = f'fit_results/plotResults_fit{args.fit_func}{toy_tag}.root'
out_tree_file = f'fit_results/fitResults_fit{args.fit_func}{toy_tag}.root'

# --- get gen S and B yields
gen_datacard = args.input_datacard.replace(args.fit_func, args.gen_func)
f_gen = ROOT.TFile(gen_datacard)
print(f'[INFO] loading gen datacard {gen_datacard}')
w_gen = f_gen.Get('w')
if not w_gen :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} workspace w not found in {gen_datacard}")
    exit(1)
# expected signal yield
Ns = w_gen.function(f'n_exp_binWTau3Mu_{category_tag}_proc_sig').getVal()
Ns_exp = args.r_gen * Ns
print(f'{ct.color_text.BLUE}[S]{ct.color_text.END} number of expected events r * Ns = {Ns_exp:,.1f}')
# expected background yield
pdf_b = w_gen.pdf(f'shapeBkg_bkg_WTau3Mu_{category_tag}')
Nb_exp = w_gen.function(f'n_exp_binWTau3Mu_{category_tag}_proc_bkg').getVal() #exp bkg yield in full region
Nb_SR_exp = Nb_exp * pdf_b.createIntegral(ROOT.RooArgSet(w_gen.var('tau_fit_mass')), 
                                          ROOT.RooFit.NormSet(ROOT.RooArgSet(w_gen.var('tau_fit_mass'))), 
                                          ROOT.RooFit.Range("sig_range")).getVal()
print(f'{ct.color_text.BLUE}[B]{ct.color_text.END} number of expected events Nb = {Nb_exp:,.1f} --> Nb_SR = {Nb_SR_exp:,.1f}')
f_gen.Close()

# --- get S+B workspace
# get workspace from datacard
f = ROOT.TFile(args.input_datacard)
w = f.Get('w')
if not w :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} workspace w not found in {args.input_datacard}")
    exit(1)
print(f'[INFO] workspace {w.GetName()} loaded from {args.input_datacard}')
mass = w.var('tau_fit_mass')

# SIGNAL MODEL
pdf_s = w.pdf(f'shapeSig_sig_WTau3Mu_{category_tag}')
if not pdf_s :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} pdf shapeBkg_sig_WTau3Mu_{category_tag} not found in {args.input_datacard}")
    exit(1)
## expected signal yield
#Ns = w.function(f'n_exp_binWTau3Mu_{category_tag}_proc_sig').getVal()
#Ns_exp = args.r_gen * Ns
#print(f'{ct.color_text.BLUE}[S]{ct.color_text.END} number of expected events r * Ns = {Ns_exp:,.1f}')

# BACKGROUND MODEL
pdf_b = w.pdf(f'shapeBkg_bkg_WTau3Mu_{category_tag}')
if not pdf_b :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} pdf n_exp_binWTau3Mu_{category_tag}_proc_bkg not found in {args.input_datacard}")
    exit(1)
#Nb_exp = w.function(f'n_exp_binWTau3Mu_{category_tag}_proc_bkg').getVal() #exp bkg yield in full region
#print(f'{ct.color_text.BLUE}[B]{ct.color_text.END} number of expected events Nb = {Nb_exp:,.1f}')

# FULL MODEL
Ns_fit = ROOT.RooRealVar('Ns_fit', 'Ns_fit', -10, 10)#Ns_exp + 0.5, -10*Ns_exp - 3.0, 10*Ns_exp + 3.0)
Nb_fit = ROOT.RooRealVar('Nb_fit', 'Nb_fit', Nb_exp + 0.5, 0, 100)
pdf_sb = ROOT.RooAddPdf('pdf_sb', 'pdf_sb', 
                        ROOT.RooArgList(pdf_s, pdf_b), 
                        ROOT.RooArgList(Ns_fit, Nb_fit))
print('\n')

# --- bias setup
i_success_toys = np.array([], dtype=int)
Ns_fit_list, NsE_fit_list = np.array([]), np.array([])
Nb_fit_list, NbE_fit_list = np.array([]), np.array([])
N_SR_exp_list = np.array([])
N_SR_fit_list, N_SR_E_fit_list = np.array([]), np.array([])
N_failed_fit = 0

# --- loop on toy datasets and fit
frame_base = mass.frame()
toy_file = ROOT.TFile(f'toys/{toys_file_name}')
out_file = ROOT.TFile(out_plot_file, 'recreate')
for i in range(1, Ntoy_to_process+1) :
    
    # get toy dataset
    toy_file.cd()
    toy_dataset = toy_file.Get(f'toys/toy_{i}')
    if not toy_dataset :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} toy dataset {i} not found in {toys_file_name}")
        exit(1)
    print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} toy {i} loaded')

    # checks on toy dataset
    if toy_dataset.numEntries() == 0 :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} toy dataset {i} is empty")
        N_failed_fit += 1
        continue
    
    # fit toy dataset and check status
    result = pdf_sb.fitTo(
        toy_dataset,
        ROOT.RooFit.Save(),
        PrintLevel=-1,
    )
    print(f'{ct.color_text.BOLD}[FIT]{ct.color_text.END} toy {i} fit status = {result.status()}')
    if result.status() != 0 :
        print(f'{ct.color_text.RED}[ERROR]{ct.color_text.END} fit failed for toy {i}')
        N_failed_fit += 1
        continue
    i_success_toys = np.append(i_success_toys,i)
    # save fit results
    #N_SR_exp_list = np.append(N_SR_exp_list, toy_dataset.sumEntries("", "sig_range"))
    N_SR_exp_list = np.append(N_SR_exp_list, Ns_exp + Nb_SR_exp)
    N_SR_fit_list = np.append(N_SR_fit_list, 
                              Ns_fit.getVal()*pdf_s.createIntegral(ROOT.RooArgSet(mass), ROOT.RooFit.NormSet(ROOT.RooArgSet(mass)), ROOT.RooFit.Range("sig_range")).getVal() + Nb_fit.getVal()*pdf_b.createIntegral(ROOT.RooArgSet(mass), ROOT.RooFit.NormSet(ROOT.RooArgSet(mass)), ROOT.RooFit.Range("sig_range")).getVal())
    Ns_fit_list  = np.append(Ns_fit_list,  Ns_fit.getVal())
    NsE_fit_list = np.append(NsE_fit_list, Ns_fit.getError())
    Nb_fit_list  = np.append(Nb_fit_list,  Nb_fit.getVal())
    NbE_fit_list = np.append(NbE_fit_list, Nb_fit.getError())

    frame = frame_base.emptyClone('frame')
    toy_dataset.plotOn(frame)
    pdf_sb.plotOn(frame)
    out_file.cd()
    c = ROOT.TCanvas(f'c_toy_{i}', 'c_toy_{i}', 800, 600)
    frame.Draw()
    c.Write()

# --- close files
toy_file.cd()
toy_file.Close()
out_file.cd()
out_file.Close()

# --- print results
print('\n')
print(f'{ct.color_text.BOLD}[RESULTS]{ct.color_text.END} {Ntoy_to_process} toys fit porcessed - Ns(gen): {Ns_exp:,.1f} Nb(gen): {Nb_exp:,.1f}')
print(f'{ct.color_text.BLUE}[S]{ct.color_text.END} Ns = {np.mean(Ns_fit_list):,.1f} +/- {np.std(Ns_fit_list):,.1f}')
print(f'{ct.color_text.BLUE}[B]{ct.color_text.END} Nb = {np.mean(Nb_fit_list):,.1f} +/- {np.std(Nb_fit_list):,.1f}')
print(f'{ct.color_text.GREEN}[SUCCESS]{ct.color_text.END} {Ntoy_to_process - N_failed_fit} ({(Ntoy_to_process - N_failed_fit)/Ntoy_to_process*100:,.2f} % ) fits successfull')
print(f'{ct.color_text.RED}[FAILED]{ct.color_text.END} {N_failed_fit} fits failed')

# --- save results in tree
col_names = ['i_toy', 'Ns_gen', 'Ns_fit', 'Ns_fit_err', 'Nb_gen', 'Nb_fit', 'Nb_fit_err', 'N_SR_fit', 'N_SR_gen', 'r_gen', 'r_fit', 'r_fit_err']

#i_toy = np.array(i_success_toys, dtype=int)

Ns_exp = np.array([Ns_exp]*len(Ns_fit_list), dtype=float)
#Ns_fit = np.array(Ns_fit_list, dtype=float)
#Ns_fit_err = np.array(NsE_fit_list, dtype=float)

r_gen = np.array([args.r_gen]*len(Ns_fit_list), dtype=float)
r_fit = Ns_fit_list/Ns
r_fit_err = NsE_fit_list/Ns

Nb_exp = np.array([Nb_exp]*len(Nb_fit_list), dtype=float)
#Nb_fit = np.array(Nb_fit_list, dtype=float)
#Nb_fit_err = np.array(NbE_fit_list, dtype=float)

df = ROOT.RDF.FromNumpy(dict(zip(col_names, [i_success_toys, Ns_exp, Ns_fit_list, NsE_fit_list, Nb_exp, Nb_fit_list, NbE_fit_list, N_SR_fit_list, N_SR_exp_list,  r_gen, r_fit, r_fit_err])))
df.Snapshot('fit_results', out_tree_file)
print(f'{ct.color_text.BOLD}[RESULTS]{ct.color_text.END} fit results saved in {out_tree_file}')