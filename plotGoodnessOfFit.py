#!/usr/bin/env python3

import argparse
import json
import math
from pathlib import Path
import os, sys
import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(description="Plot Combine goodness-of-fit results")
parser.add_argument("-i", "--input",        dest="input",                   default="gof.json",             help="Input JSON file with goodness-of-fit results")
parser.add_argument("-e", "--era",          dest="era",                     default="2022",                 help="Era to process, e.g. 2022, 2022EE, 2022+2023, etc.")
parser.add_argument("-j", "--jsonInput",    dest="jsonInput",               default="settings.json",        help="Settings JSON file")
parser.add_argument("-m", "--massPoint",    dest="massPoint",   type=int,   default=700,                    help="Tprime mass point")
parser.add_argument("--bins",               dest="bins",        type=int,   default=30,                     help="Number of bins for the histogram")
parser.add_argument("--title",              dest="title",                   default="",                     help="Title of the plot")
args = parser.parse_args()

with open(args.input) as input_file:
    result      = json.load(input_file)["125.0"]
with open(args.jsonInput) as file:
    jsonInput   = json.load(file)

outputFolder    = Path(args.input).parent
era             = args.era
mass            = args.massPoint
lumi            = jsonInput["lumi_dict"][era]
toys            = result["toy"]
observed        = result["obs"][0]
p_value         = sum(toy >= observed for toy in toys) / len(toys)

toy_min, toy_max = min(toys), max(toys)
toy_padding = 0.05 * (toy_max - toy_min)
hist = ROOT.TH1D(
    "gof_toys",
    "",
    args.bins,
    toy_min - toy_padding,
    toy_max + toy_padding,
)
for toy in toys:
    hist.Fill(toy)

x_min = min(hist.GetXaxis().GetXmin(), observed)
x_max = max(hist.GetXaxis().GetXmax(), observed)
x_padding = 0.04 * (x_max - x_min)
y_max = 1.35 * hist.GetMaximum()

CMS.SetExtraText("Work in progress")
CMS.SetLumi(lumi, run=None)
CMS.SetEnergy(13.6)
CMS.ResetAdditionalInfo()
canvas = CMS.cmsCanvas(
    "gof_canvas",
    x_min - x_padding,
    x_max + x_padding,
    0,
    y_max,
    "Goodness-of-fit test statistic",
    "Pseudo-experiments",
    square=True,
    iPos=0,
)

blue    = ROOT.TColor.GetColor("#5790fc")
red     = ROOT.TColor.GetColor("#e42536")
CMS.cmsDraw(hist, "HIST", lcolor=blue, lwidth=2, fcolor=blue, alpha=0.65)

observed_line = ROOT.TLine(observed, 0, observed, y_max)
CMS.cmsDrawLine(observed_line, lcolor=red, lstyle=ROOT.kDashed, lwidth=3)

legend = CMS.cmsLeg(0.48, 0.77, 0.90, 0.92, textSize=0.035)
legend.AddEntry(hist,           f"Pseudo-experiments ({len(toys)})",    "f")
legend.AddEntry(observed_line,  f"Observed = {observed:.3g}",           "l")
legend.AddEntry(ROOT.nullptr,   f"p-value = {p_value:.3f}",             "")
legend.Draw()

# label = ROOT.TLatex()
# label.SetNDC()
# label.SetTextFont(42)
# label.SetTextSize(0.04)
# label.DrawLatex(0.19, 0.84, args.title)
# label.DrawLatex(0.58, 0.62, f"p-value = {p_value:.3f}")

print(f"Saving plot to {outputFolder}/gof_plot.png and {outputFolder}/gof_plot.pdf")
CMS.SaveCanvas(canvas, f"{outputFolder}/gof_plot.png", False)
CMS.SaveCanvas(canvas, f"{outputFolder}/gof_plot.pdf")
