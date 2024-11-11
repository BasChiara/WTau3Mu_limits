import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
import numpy as np
import os
# my imports
import utils
import sys
sys.path.append('..')
import style.color_text as ct

# --- argument pareser
parser = utils.get_arguments()
parser.add_argument('--input_root', dest='input_root',  type=str, default='', help='input root file with fit results')
parser.add_argument('--out_root',   dest='out_root',    type=str, default='', help='out root file with pulls')
parser.add_argument('-m', '--method', choices=['combine', 'roofit'],    type=str, default='combine', help='method used for fit')
parser.add_argument('--plot_outdir', dest='plot_outdir', type=str, default='plots', help='output directory for plots')
args = parser.parse_args()
print(args)
print('\n')

 # --- setup
N_toys  = args.nToys
r_truth = args.r_gen
truth_function  = args.gen_func
fit_function    = args.fit_func
name = f'gen_{truth_function}_fit_{fit_function}_r{r_truth:,.1f}_{args.tag}_{args.method}'
canv = ROOT.TCanvas('canv', 'canv', 800, 600)

# --- function to plot pulls
def plot_pulls(canv, name = 'r', r_truth = 1.0, text = True, mean = 0.0, mean_error = 0.0, sigma = 1.0, sigma_error = 0.0, chi2_nDoF = 1.0):

    canv.Update()
    if text:
        fit_text = ROOT.TLatex()
        fit_text.SetTextSize(0.04)
        fit_text.SetTextFont(42)
        fit_text.SetNDC()
        fit_text.DrawLatex(0.15, 0.85, f"r_{{truth}} = {r_truth:.2f}")
        fit_text.DrawLatex(0.15, 0.80, f"Mean = {mean:.3f} #pm {mean_error:.3f}")
        fit_text.DrawLatex(0.15, 0.75, f"Sigma = {sigma:.3f} #pm {sigma_error:.3f}")
        fit_text.DrawLatex(0.15, 0.70, "#chi^{2}/ndf = %.2f" %chi2_nDoF)
        fit_text.DrawLatex(0.70, 0.85, args.tag)

    canv.Update()
    canv.SaveAs(f'{args.plot_outdir}/pull_{name}.png')
    canv.SaveAs(f'{args.plot_outdir}/pull_{name}.pdf')


if args.method == 'combine':
    # --- preliminary checks
    # check if input root exists and is correct
    if not os.path.isfile(args.input_root) :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} input root file {args.input_root} not found")
        exit(1)
    elif 'MultiDimFit' not in args.input_root:
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} input root file {args.input_root} must be produced with MultiDimFit")
        exit(1)

   
    # Open file with fits
    f = ROOT.TFile(args.input_root)
    t = f.Get("limit")

    # histograms
    pull_nbins, pull_low, pull_high = 40, -5, 5
    r_nbins, r_low, r_high = 100, -20, 20
    sigma_nbins, sigma_low, sigma_high = 25, 0, 5

    hist_pull = ROOT.TH1F("pull_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), pull_nbins, pull_low, pull_high)
    hist_pull.GetXaxis().SetTitle("Pull = (r_{fit}-r_{truth})/#sigma_{fit}")
    hist_pull.GetYaxis().SetTitle("Entries")
    hist_rfit = ROOT.TH1F("rfit_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), r_nbins, r_low, r_high)
    hist_sigmafit = ROOT.TH1F("sigmafit_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), sigma_nbins, sigma_low, sigma_high)
    hist_rVSsigma_fit = ROOT.TH2F("rVSsigma_fit_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), r_nbins, r_low, r_high, sigma_nbins, sigma_low, sigma_high)
    hist_rVSsigma_fit.GetXaxis().SetTitle("r_{fit}")
    hist_rVSsigma_fit.GetYaxis().SetTitle("#sigma_{fit}")
    hist_pullVSr_fit = ROOT.TH2F("pullVSr_fit_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), r_nbins, r_low, r_high, pull_nbins, pull_low, pull_high)
    hist_pullVSr_fit.GetXaxis().SetTitle("r_{fit}")
    hist_pullVSr_fit.GetYaxis().SetTitle("Pull = (r_{fit}-r_{truth})/#sigma_{fit}")
    hist_pullVSsigma_fit = ROOT.TH2F("pullVSsigma_fit_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), sigma_nbins, sigma_low, sigma_high, pull_nbins, pull_low, pull_high)
    hist_pullVSsigma_fit.GetXaxis().SetTitle("#sigma_{fit}")
    hist_pullVSsigma_fit.GetYaxis().SetTitle("Pull = (r_{fit}-r_{truth})/#sigma_{fit}")
    

    sigma_values = np.array([])
    Nfailed = 0
    for i_toy in range(t.GetEntries() // 3):
        # Best-fit value
        t.GetEntry(i_toy * 3)
        r_fit = getattr(t, "r")
     
        # -1 sigma value
        t.GetEntry(i_toy * 3 + 1)
        r_lo = getattr(t, "r")

        # +1 sigma value
        t.GetEntry(i_toy * 3 + 2)
        r_hi = getattr(t, "r")

        

        diff = r_fit - r_truth
        #sigma = (r_hi - r_lo) / 2
         # skip failed fits
        #if sigma > 50:
        #    Nfailed += 1
        #    continue
        
        # Use uncertainty depending on where mu_truth is relative to mu_fit
        if diff > 0:
            sigma = abs(r_hi - r_fit)
        else:
            sigma = abs(r_lo - r_fit)

        if sigma != 0:
            sigma_values = np.append(sigma_values, sigma)
        else:
            sigma = sigma_values.mean()

        if sigma != 0:
            hist_pull.Fill(diff / sigma)
            hist_rfit.Fill(r_fit)
            hist_sigmafit.Fill(sigma)
            hist_rVSsigma_fit.Fill(r_fit, sigma)
            hist_pullVSr_fit.Fill(r_fit, diff / sigma)
            hist_pullVSsigma_fit.Fill(sigma, diff / sigma)
    
    print(f"{ct.color_text.BOLD}[i]{ct.color_text.END} failed fits rate : {Nfailed/N_toys*100:.2f} %")
    # save pull histogram in file
    f_out = ROOT.TFile(args.out_root, 'RECREATE')
    hist_pull.Write()
    hist_rfit.Write()
    hist_sigmafit.Write()
    hist_rVSsigma_fit.Write()
    hist_pullVSr_fit.Write()
    hist_pullVSsigma_fit.Write()
    f_out.Close()

    # draw pull histogram
    hist_pull.SetLineColor(ROOT.kBlack)
    hist_pull.SetLineWidth(2)
    #hist_pull.Draw()
    # Fit Gaussian to pull distribution
    ROOT.gStyle.SetOptFit(111)
    #hist_pull.Fit("gaus")
    # fit with a crystal ball -> account for tails
    pull    = ROOT.RooRealVar("pull", "pull", pull_low, pull_high)
    pull.setRange("fit_range", -3.0, 2.0)
    pull.setRange("full_range", pull_low, pull_high)
    mean    = ROOT.RooRealVar("mean", "mean", 0, 0.001, 1)
    sigma   = ROOT.RooRealVar("sigma", "sigma", 1.0, 0.2, 5)
    alpha   = ROOT.RooRealVar("alpha", "alpha", 1, 0, 10)
    n       = ROOT.RooRealVar("n", "n", 10, 0, 200)
    cb      = ROOT.RooCBShape("cb", "cb", pull, mean, sigma, alpha, n)
    gaus    = ROOT.RooGaussian("gaus", "gaus", pull, mean, sigma)
    data    = ROOT.RooDataHist("data", "data", ROOT.RooArgList(pull), hist_pull)

    pdf_to_fit = cb if r_truth < 20.0 else gaus

    #fit and save results
    results = pdf_to_fit.fitTo(
        data,
        ROOT.RooFit.Range("fit_range"),
        ROOT.RooFit.Save(),
        ROOT.RooFit.PrintLevel(-1),
    )
    results.Print()

    pull_frame = pull.frame()
    # plot on the full range

    data.plotOn(
        pull_frame,
        ROOT.RooFit.MarkerColor(ROOT.kBlack),
        ROOT.RooFit.MarkerStyle(20),
    )
    pull_frame.SetTitle(hist_pull.GetTitle())
    #check if fit converged
    if results.status() > 1:
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} fit did not converge")
    else:
        pdf_to_fit.plotOn(
            pull_frame,
            ROOT.RooFit.LineColor(ROOT.kRed),
            ROOT.RooFit.MoveToBack(),
            ROOT.RooFit.Range("full_range"),
        )
    canv.cd()
    pull_frame.Draw()
    pull_frame.SetTitle(hist_pull.GetTitle())
    pull_frame.GetXaxis().SetTitle(hist_pull.GetXaxis().GetTitle())
    pull_frame.GetYaxis().SetTitle(hist_pull.GetYaxis().GetTitle())
    chi2_nDoF = pull_frame.chiSquare()
    
    plot_pulls(canv, name, r_truth, mean=mean.getVal() , mean_error=mean.getError(), sigma=sigma.getVal(), sigma_error=sigma.getError(), chi2_nDoF=chi2_nDoF)

elif args.method == 'roofit':

    # check if input root exists and is correct
    if not os.path.isfile(args.input_root) :
        print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} input root file {args.input_root} not found")
        exit(1)
    
    # Open file with fits
    fit_rdf = ROOT.RDataFrame("fit_results", args.input_root)
    print(f"{ct.color_text.BOLD}[+]{ct.color_text.END} input root file {args.input_root} ")

    pull =  fit_rdf.Define("pull_Ns", '(Ns_gen - Ns_fit)/Ns_fit_err').Histo1D(("pull_r", "pull_r", 32, -4, 4), "pull_Ns").GetPtr()
    pull.SetTitle(f"pull r, truth={truth_function}, fit={fit_function}")
    pull.GetXaxis().SetTitle("Pull = (r_{truth}-r_{fit})/#sigma_{fit}")
    pull.GetYaxis().SetTitle("Entries")
    pull.SetLineColor(ROOT.kBlack)
    pull.SetLineWidth(2)
   
    # fit with gaussian and fet results
    pull.Fit("gaus")
    fit = pull.GetFunction("gaus")
    mean = fit.GetParameter(1)
    mean_error = fit.GetParError(1)
    sigma = fit.GetParameter(2)
    sigma_error = fit.GetParError(2)
    chi2_nDoF = fit.GetChisquare()/fit.GetNDF()

    canv.cd()
    pull.Draw()
    plot_pulls(canv, name, r_truth, mean=mean, mean_error=mean_error, sigma=sigma, sigma_error=sigma_error, chi2_nDoF=chi2_nDoF)

    pull_B =  fit_rdf.Define("pull_Nb", '(Nb_gen - Nb_fit)/Nb_fit_err').Histo1D(("pull_B", "pull_B", 32, -4, 4), "pull_Nb").GetPtr()
    pull_B.SetTitle(f"pull B, truth={truth_function}, fit={fit_function}")
    pull_B.GetXaxis().SetTitle("Pull = (B_{truth}-B_{fit})/#sigma_{fit}")
    pull_B.GetYaxis().SetTitle("Entries")
    pull_B.SetLineColor(ROOT.kBlack)
    pull_B.SetLineWidth(2)
    # fit with gaussian and fet results
    pull_B.Fit("gaus")
    fit_B = pull_B.GetFunction("gaus")
    mean_B = fit_B.GetParameter(1)
    mean_error_B = fit_B.GetParError(1)
    sigma_B = fit_B.GetParameter(2)
    sigma_error_B = fit_B.GetParError(2)
    chi2_nDoF_B = fit_B.GetChisquare()/fit_B.GetNDF()

    canv.cd()
    pull_B.Draw()
    plot_pulls(canv, name+'_B', r_truth, mean=mean_B, mean_error=mean_error_B, sigma=sigma_B, sigma_error=sigma_error_B, chi2_nDoF=chi2_nDoF_B)
