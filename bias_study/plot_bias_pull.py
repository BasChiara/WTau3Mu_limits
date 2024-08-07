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
args = parser.parse_args()
print(args)
print('\n')

# --- preliminary checks
# check if input root exists and is correct
if not os.path.isfile(args.input_root) :
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} input root file {args.input_root} not found")
    exit(1)
elif 'MultiDimFit' not in args.input_root:
    print(f"{ct.color_text.RED}[ERROR]{ct.color_text.END} input root file {args.input_root} must be produced with MultiDimFit")
    exit(1)

# --- setup
N_toys  = args.nToys
r_truth = args.r_gen
truth_function  = args.gen_func
fit_function    = args.fit_func
name = f'gen_{truth_function}_fit_{fit_function}_r{r_truth:,.1f}_{args.tag}'

# Open file with fits
f = ROOT.TFile(args.input_root)
t = f.Get("limit")

hist_pull = ROOT.TH1F("pull_%s" % name, "truth=%s, fit=%s" % (truth_function, fit_function), 32, -4, 4)
hist_pull.GetXaxis().SetTitle("Pull = (r_{truth}-r_{fit})/#sigma_{fit}")
hist_pull.GetYaxis().SetTitle("Entries")

sigma_values = np.array([])
Nfailed = 0
for i_toy in range(N_toys):
    # Best-fit value
    t.GetEntry(i_toy * 3)
    r_fit = getattr(t, "r")
    
    # -1 sigma value
    t.GetEntry(i_toy * 3 + 1)
    r_lo = getattr(t, "r")

    # +1 sigma value
    t.GetEntry(i_toy * 3 + 2)
    r_hi = getattr(t, "r")

    # skip failed fits
    
    if r_lo <  1e-5:
        Nfailed += 1
        continue


    diff = r_truth - r_fit
    if r_fit < 0.011:
        sigma = abs(r_hi-r_fit)
    else:
        sigma = (r_hi - r_lo) / 2
    # Use uncertainty depending on where mu_truth is relative to mu_fit
    #if diff > 0:
    #    sigma = abs(r_hi - r_fit)
    #else:
    #    sigma = abs(r_lo - r_fit)

    if sigma != 0:
        sigma_values = np.append(sigma_values, sigma)
    else:
        sigma = sigma_values.mean()

    if sigma != 0:
        hist_pull.Fill(diff / sigma)
print(f"{ct.color_text.BOLD}[i]{ct.color_text.END} failed fits rate : {Nfailed/N_toys*100:.2f} %")
# save pull histogram in file
f_out = ROOT.TFile(args.out_root, 'RECREATE')
hist_pull.Write()
f_out.Close()

# draw pull histogram
canv = ROOT.TCanvas('canv', 'canv', 800, 600)
hist_pull.SetLineColor(ROOT.kBlack)
hist_pull.SetLineWidth(2)
#hist_pull.Draw()
# Fit Gaussian to pull distribution
ROOT.gStyle.SetOptFit(111)
#hist_pull.Fit("gaus")
# fit with a crystal ball -> account for tails
pull    = ROOT.RooRealVar("pull", "pull", -4, 4)
mean    = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
sigma   = ROOT.RooRealVar("sigma", "sigma", 1.5, 0.5, 5)
alpha   = ROOT.RooRealVar("alpha", "alpha", 1, -10, 10)
n       = ROOT.RooRealVar("n", "n", 10, 0, 1000)
cb      = ROOT.RooCBShape("cb", "cb", pull, mean, sigma, alpha, n)
gaus    = ROOT.RooGaussian("gaus", "gaus", pull, mean, sigma)
data    = ROOT.RooDataHist("data", "data", ROOT.RooArgList(pull), hist_pull)

pdf_to_fit = cb if r_truth < 20.0 else gaus

#pdf_to_fit.fitTo(data)

pull_frame = pull.frame()
data.plotOn(
    pull_frame,
    ROOT.RooFit.MarkerColor(ROOT.kBlack),
    ROOT.RooFit.MarkerStyle(20),
)
pull_frame.SetTitle(hist_pull.GetTitle())
#pdf_to_fit.plotOn(
#    pull_frame,
#    ROOT.RooFit.LineColor(ROOT.kRed),
#    #ROOT.RooFit.MoveToBack(),
#)
pull_frame.Draw()
pull_frame.SetTitle(hist_pull.GetTitle())
pull_frame.GetXaxis().SetTitle(hist_pull.GetXaxis().GetTitle())
pull_frame.GetYaxis().SetTitle(hist_pull.GetYaxis().GetTitle())
chi2_nDoF = 1.0#pull_frame.chiSquare()
# get fit results
#fit = hist_pull.GetFunction("gaus")
#mean = fit.GetParameter(1)
#mean_error = fit.GetParError(1)
#sigma = fit.GetParameter(2)
#sigma_error = fit.GetParError(2)
#chi2_nDoF = fit.GetChisquare()/fit.GetNDF()
canv.Update()
fit_text = ROOT.TLatex()
fit_text.SetTextSize(0.04)
fit_text.SetTextFont(42)
fit_text.SetNDC()
fit_text.DrawLatex(0.15, 0.85, f"r_{{truth}} = {r_truth:.2f}")
fit_text.DrawLatex(0.15, 0.80, f"Mean = {mean.getVal():.3f} #pm {mean.getError():.3f}")
fit_text.DrawLatex(0.15, 0.75, f"Sigma = {sigma.getVal():.3f} #pm {sigma.getError():.3f}")
fit_text.DrawLatex(0.15, 0.70, "#chi^{2}/ndf = %.2f" %chi2_nDoF)

canv.Update()
canv.SaveAs(f'plots/pull_{name}.png')
canv.SaveAs(f'plots/pull_{name}.pdf')

