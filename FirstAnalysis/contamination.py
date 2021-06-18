#!/usr/bin/env python

from ROOT import TFile

from hfplot.plot_spec_root import ROOTFigure
from hfplot.root_helpers import create_name
from hfplot.style import StyleObject1D



# gStyle.SetOptStat(0)
# gStyle.SetErrorX(0)
# gStyle.SetFrameLineWidth(1)
# gStyle.SetTitleSize(0.045, "x")
# gStyle.SetTitleSize(0.045, "y")
# gStyle.SetMarkerSize(1)
# gStyle.SetLabelOffset(0.015, "x")
# gStyle.SetLabelOffset(0.02, "y")
# gStyle.SetTickLength(-0.02, "x")
# gStyle.SetTickLength(-0.02, "y")
# gStyle.SetTitleOffset(1.1, "x")
# gStyle.SetTitleOffset(1.0, "y")




# def kinematic_plots(var, particle, detector, hp):
#     fileo2 = TFile(PATH_FILE)
#     cres = TCanvas("cres", "resolution distribution")
#     cres.SetCanvasSize(1600, 1000)
#     cres.cd()
#     num = fileo2.Get(
#         "qa-tracking-rejection-%s/tracking%ssel%s/%seta" % (particle, detector, hp, var)
#     )
#     den = fileo2.Get("qa-tracking-rejection-%s/tracking/%seta" % (particle, var))
#     # gPad.SetLogz()
#     num.Divide(den)
#     num.Draw("coltz")
#     num.GetYaxis().SetTitle("#eta")
#     num.GetYaxis().SetTitleOffset(1.0)
#     num.GetZaxis().SetRangeUser(0.01, 1)
#     num.SetTitle("Fraction of %s selected by %s as %s" % (particle, detector, hp))
#     saveCanvas(
#         cres, "contamination/%seta_%sSelfrom%sas%s" % (var, particle, detector, hp)
#     )


PATH_FILE = "../codeHF/AnalysisResults_O2.root"

EXTENSIONS_IMAGE = (".pdf", ".png")

def ratioparticle(
    var="pt",
    numname="Electron",
    selnum="RICHSelHpElLoose",
    denname="Pion",
    selden="RICHSelHpElLoose",
    label="e/#pi",
):
    # Read and prepare histograms
    fileo2 = TFile(PATH_FILE)
    num2d = fileo2.Get(f"qa-rejection-general/h{numname}{selnum}/{var}eta")
    den2d = fileo2.Get(f"qa-rejection-general/h{denname}{selden}/{var}eta")
    num = num2d.ProjectionX(create_name(num2d), 1, num2d.GetXaxis().GetNbins())
    den = den2d.ProjectionX(create_name(den2d), 1, den2d.GetXaxis().GetNbins())
    num.Divide(den)

    # Define the figure
    figure = ROOTFigure(1, 1, size=(1600, 900))
    figure.define_plot(y_log=True, title="resolution distribution")
    figure.add_object(num, style=StyleObject1D(draw_options="colz"))
    figure.axes("x", title="p_{T}")
    figure.axes("y", title=label, title_offset=1.4)
    figure.create()

    # Save
    save_path = f"rejection/FractionOf_{numname}_{selnum}_Over_{denname}_{selden}"
    for ext in EXTENSIONS_IMAGE:
        figure.save(f"{save_path}{ext}")


def is_e_not_pi_plots(particle):
    fileo2 = TFile(PATH_FILE)
    task = "qa-rejection-general"
    hist = "pteta"

    # Extract histograms
    hist_gm = fileo2.Get(f"{task}/h{particle}RICHSelHpElTight/{hist}")
    hist_alt = fileo2.Get(f"{task}/h{particle}RICHSelHpElTightAlt/{hist}")
    hist_diff = fileo2.Get(f"{task}/h{particle}RICHSelHpElTightAltDiff/{hist}")

    # Define the figure
    style = StyleObject1D(draw_options="colz")
    figure = ROOTFigure(2, 2, size=(1600, 900))
    figure.define_plot(title=f"{particle} isRICHElTight")
    figure.add_object(hist_gm, style=style)
    figure.define_plot(title=f"{particle} isElectronAndNotPion")
    figure.add_object(hist_alt, style=style)
    figure.define_plot(title=f"{particle} isRICHElTight != isElectronAndNotPion")
    figure.add_object(hist_diff, style=style)
    figure.create()

    save_path = f"contamination/is_e_not_pi_{particle}"
    for ext in EXTENSIONS_IMAGE:
        figure.save(f"{save_path}{ext}")


# kinematic_plots("p", "pion", "MID", "Muon")
# kinematic_plots("p", "mu", "MID", "Muon")
# kinematic_plots("p", "pion", "TOF", "Electron")
# kinematic_plots("p", "pion", "RICH", "Electron")
# kinematic_plots("pt", "pion", "RICH", "Electron")
# kinematic_plots("p", "kaon", "RICH", "Electron")
# kinematic_plots("pt", "kaon", "RICH", "Electron")
# kinematic_plots("p", "pion", "TOF", "Kaon")
# kinematic_plots("p", "pion", "RICH", "Kaon")

ratioparticle(
    "pt", "Electron", "RICHSelHpElTight", "Electron", "NoSel", "e/e RICHSelHpElTight"
)
ratioparticle("pt", "Electron", "NoSel", "Pion", "NoSel", "e/#pi No cuts")
ratioparticle(
    "pt", "Electron", "RICHSelHpElTight", "Pion", "RICHSelHpElTight", "Tight e/#pi "
)
ratioparticle("pt", "Muon", "MID", "Pion", "MID", "MIDSel")
ratioparticle("pt", "Pion", "RICHSelHpElTight", "Pion", "NoSel", "Contamination")
ratioparticle("pt", "Pion", "MID", "Pion", "NoSel", "Contamination MID")

ratioparticle(
    "pt",
    "Electron",
    "RICHSelHpElTightAlt",
    "Electron",
    "RICHSelHpElTight",
    "e isElectronAndNotPion/RICHSelHpElTight",
)
ratioparticle(
    "pt",
    "Electron",
    "RICHSelHpElTightAlt",
    "Pion",
    "RICHSelHpElTightAlt",
    "isElectronAndNotPion e/#pi",
)


for p in ("Electron", "Pion", "Kaon", "Muon"):
    is_e_not_pi_plots(p)
