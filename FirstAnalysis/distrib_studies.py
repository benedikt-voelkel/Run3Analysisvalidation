#!/usr/bin/env python
import os
from math import ceil, sqrt

import yaml
from ROOT import TH2F, TCanvas, TFile, TLatex, TLegend, gPad, gROOT, gStyle

from hfplot.plot_spec_root import ROOTFigure

def makeSavePaths(canvas, title, *fileFormats, outputdir="outputPlots"):
    """
    Saves the canvas as the desired output format in an output directory (default = outputPlots)
    """
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    return [outputdir + "/" + title + fileFormat for fileFormat in fileFormats]


def distr_studies(hadron="Xi_cc", collision="pp14p0", yrange="absy1p44"):
    gROOT.SetBatch(1)
    """
    Make distribution comparisons
    """
    with open(r"database.yaml") as database:
        param = yaml.load(database, Loader=yaml.FullLoader)
    latexcand = param[hadron][collision][yrange]["latexcand"]
    inputBkg = param[hadron][collision][yrange]["inputBkg"]
    inputSig = param[hadron][collision][yrange]["inputSig"]
    dirname = param[hadron][collision][yrange]["dirname"]
    normalized = param[hadron][collision][yrange]["normalized"]
    lvarlist = param[hadron][collision][yrange]["varlist"]
    lvarlatex = param[hadron][collision][yrange]["varlatex"]
    lhistonamesig = param[hadron][collision][yrange]["histonamesig"]
    lhistonamebkg = param[hadron][collision][yrange]["histonamebkg"]
    lymin = param[hadron][collision][yrange]["ymin"]
    lymax = param[hadron][collision][yrange]["ymax"]
    lxmin = param[hadron][collision][yrange]["xmin"]
    lxmax = param[hadron][collision][yrange]["xmax"]
    lrebin = param[hadron][collision][yrange]["rebin"]
    ldolog = param[hadron][collision][yrange]["dolog"]
    ldologx = param[hadron][collision][yrange]["dologx"]

    formats = [".pdf", ".root", ".C"]  # fileformats
    fileBkg = TFile(inputBkg)
    fileSig = TFile(inputSig)
    gStyle.SetOptStat(0)

    lhistosig = []
    lhistobkg = []
    nPtBins = 0
    lhemptyvar = []
    lptMin = []
    lptMax = []

    # Define some styles
    style_sig = ROOTStyle1D()
    style_sig.linecolor = 2
    style_sig.draw_option = "HIST"
    bkg_style = ROOTStyle1D()
    bkg_style.linecolor = 1
    bkg_style.draw_option = "HIST"


    for index, var in enumerate(lvarlist):
        ymin = lymin[index]
        ymax = lymax[index]
        xmin = lxmin[index]
        xmax = lxmax[index]
        varlatex = lvarlatex[index]
        lhistosigvar = []
        lhistobkgvar = []
        histonamesig = lhistonamesig[index]
        histonamebkg = lhistonamebkg[index]
        hsig = fileSig.Get(f"{dirname}/{histonamesig}")
        hbkg = fileBkg.Get(f"{dirname}/{histonamebkg}")
        nPtBins = hsig.GetNbinsY()
        for iptBin in range(nPtBins):
            hsig_px = hsig.ProjectionX(
                "hsig_px_var%s_pt%d" % (var, iptBin), iptBin + 1, iptBin + 1
            )
            hbkg_px = hbkg.ProjectionX(
                "hbkg_px_var%s_pt%d" % (var, iptBin), iptBin + 1, iptBin + 1
            )
            lhistosigvar.append(hsig_px)
            lhistobkgvar.append(hbkg_px)
            # if index == 0:
            #     ptMin = hsig.GetYaxis().GetBinLowEdge(iptBin + 1)
            #     ptMax = ptMin + hsig.GetYaxis().GetBinWidth(iptBin + 1)
            #     lptMin.append(ptMin)
            #     lptMax.append(ptMax)

        lhistosig.append(lhistosigvar)
        lhistobkg.append(lhistobkgvar)

    for index, var in enumerate(lvarlist):
        n_cols_rows = ceil(sqrt(nPtBins))
        figure = ROOTFigure(n_cols_rows, n_cols_rows, row_margin=0.05, column_margin=0.05)

        dolog = ldolog[index]
        dologx = ldologx[index]
        rebin = lrebin[index]
        for iptBin in range(nPtBins):
            hist_sig = lhistosig[index][iptBin]
            hist_bkg = lhistobkg[index][iptBin]

            if rebin > 1:
                hist_sig.RebinX(rebin)
                hist_bkg.RebinX(rebin)

            nSigEntries = hist_sig.Integral()
            nBkgEntries = hist_bkg.Integral()

            if not nSigEntries or not nBkgEntries:
                print(f"ERROR: Found empty signal or background distribution for variable={var} in pT bin={iptBin}")
                continue


            if normalized:
                for ibin in range(hist_sig.GetNbinsX()):
                    bincontent = hist_sig.GetBinContent(ibin + 1)
                    hist_sig.SetBinContent(ibin + 1, bincontent / nSigEntries)
                    hist_sig.SetBinError(ibin + 1, 0.0)

                for ibin in range(hist_bkg.GetNbinsX()):
                    bincontent = hist_bkg.GetBinContent(ibin + 1)
                    hist_bkg.SetBinContent(ibin + 1, bincontent / nBkgEntries)
                    hist_bkg.SetBinError(ibin + 1, 0.0)

            figure.define_plot(x_log=dologx, y_log=dolog)

            figure.add_object(hist_sig, style=style_sig, label=f"Sig before norm ({int(nSigEntries)} entries)")
            figure.add_object(hist_bkg, style=style_bkg, label=f"Bkg before norm ({int(nBkgEntries)} entries)")
            figure.add_text(f"{lptMin[iptBin]:.1f} GeV < p_{{T}} ({latexcand}) < {lptMax[iptBin]:.1f} GeV")

        figure.create()
        for save_paths in makeSavePaths(cpt, f"distribution_{var}", *formats, outputdir=f"output_{hadron}"):
            figure.save(save_paths)


distr_studies()
