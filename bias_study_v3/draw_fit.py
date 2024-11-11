import ROOT

input_file = 'higgsCombineTest.MultiDimFit.gen_const_fit_expo_r1.0.mH1.777.root'

f = ROOT.TFile(input_file)
w = f.Get("w")
w.Print("v")

n_bins = 65
binning = ROOT.RooFit.Binning(n_bins,1.4,2.05)

can = ROOT.TCanvas()
plot = w.var("tau_fit_mass").frame()
w.data("data_obs").plotOn( plot, binning )

# Load the S+B model
sb_model = w.pdf("model_s").getPdf("pdf_binWTau3Mu_A22")

# Prefit
sb_model.plotOn( plot, ROOT.RooFit.LineColor(2))#, ROOT.RooFit.Name("prefit") )

# Postfit
w.loadSnapshot("MultiDimFit")
sb_model.plotOn( plot, ROOT.RooFit.LineColor(4))#, ROOT.RooFit.Name("postfit") )
r_bestfit = w.var("r").getVal()

plot.Draw()

leg = ROOT.TLegend(0.55,0.6,0.85,0.85)
leg.AddEntry("prefit", "Prefit S+B model (r=1.00)", "L")
leg.AddEntry("postfit", "Postfit S+B model (r=%.2f)"%r_bestfit, "L")
leg.Draw("Same")

can.Update()
can.SaveAs("gen_const_fit_expo_r1.0_sb_model.png")
