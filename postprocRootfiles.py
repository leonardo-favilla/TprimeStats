import ROOT
import os, copy

folder = "/eos/home-a/acagnott/DarkMatter/nosynch/run2022_selection/plots/"
files = os.listdir(folder)
files = [f for f in files if f.endswith(".root")]

bkgs = ["WJets", "ZJets", "TT", "QCD"]
bkg_files = {b : [f for f in files if f.startswith(b)] for b in bkgs}

var = "PuppiMET_T1_pt_nominal"

bins = ["SRTop", "AH", "SL", "AH1lWR", "AH0lZR"]

output = ROOT.TFile("histo2022.root", "RECREATE")
for b in bkg_files.keys():
    for r in bins:
        h_out = None
        for f in bkg_files[b]:
            print(f)
            input = ROOT.TFile.Open(folder + f)
            # PuppiMET_T1_pt_nominal_SRTop_
            tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_")))
            print(tmp)
            if h_out == None:
                h_out = tmp.Clone("")
            else:
                h_out.Add(tmp)
            # input.Close()
        h_out.SetName("hist_"+b+"_"+r)
        output.cd()
        h_out.Write()

output.Close()

