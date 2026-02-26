# COSA MANCA:
# - aggiungere la parte di creazione degli istogrammi dei dati, se blind si filla con la somma dei background
# - aggiungere la parte di creazione dei datacards singole per ogni bin(categoria)
# - aggiungere la parte di systematics
# Obiettivo: 
# - Creare un file di configurazione in formato JSON che contenga le informazioni necessarie per la creazione dei datacards
# - Sistemare questa amcro in modo tale che sia runnabile modificando solo settings.json

import CombineHarvester.CombineTools.ch as ch
import optparse
import json, os
from array import array

usage = 'python3 CreateDatacards.py -i inputEosFolder -u'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inputEosFolder', dest='inputEosFolder', type=str, default = '', help='Please enter a folder containing Root files to be collected, if not specified the code will take the ROOT file {} in the current directory')
parser.add_option('-u', '--unblind', dest='unblind', action='store_true', default=False, help='Unblind')
parser.add_option('-s', '--singledatacards', dest='singledatacards', action='store_true', default=False, help='Write single datacards per each bin')
parser.add_option('-j', '--jsonInput', dest='jsonInput', type=str, default="settings.json", help='json file containing the settings')
parser.add_option('-l', '--lumi', dest='lumi', type=str, default="1", help='luminosity, default 1')
parser.add_option('-e', '--era', dest='era', type=str, default="2022", help='insert era (e.g. 2022, 2022EE)')
parser.add_option('--addSyst', dest='addSyst', action='store_true', default=False, help='add Systematics in the datacards')
parser.add_option('--addMCStat', dest='addMCStat', action='store_true', default=False, help='add auto MC Stat in the datacards')
(opt, args) = parser.parse_args()
lumi = float(opt.lumi)

# Your code here
def CollectHistos(inputEosFolder, jsonInput, era):
    #  MODIFICHE DA AGGIUNGERE
    # CREARE a prescindere anche gli istogrammi dei dati, se blind si filla con la somma dei background

    import ROOT
    import os, copy

    folder = inputEosFolder
    files = os.listdir(folder)
    files = [f for f in files if f.endswith(".root")]
    bkg_files = {b : [f for f in files if f.startswith(b)] for b in jsonInput["processes"]["backgrounds"]}
    signal_files = {s : [f for f in files if f.startswith(s)] for s in jsonInput["processes"]["signals"]}
    if unblind: 
        data_files = [f for f in files if f.startswith("Data")]
    else:
        data_files = jsonInput["processes"]["backgrounds"]

    var = jsonInput["variable"]
    bins = jsonInput["categories"]
    print("Variable for fit: ", var)
    print("Regions: ", bins)
    if opt.addSyst:
        systs = []
        systs.append("nominal")
        for syst in jsonInput["systematics"]:
            if jsonInput["systematics"][syst]['type'] == 'shape':
                systs.append(jsonInput["systematics"][syst]['branchRootFile'])

    if not os.path.exists(era):
        os.makedirs(era)
    output = ROOT.TFile(f"{era}/histo{era}.root", "RECREATE")
    
    if opt.addSyst:
        for syst in systs:
            if syst == "nominal":
                var_type = [""]
            else:
                var_type = ["_up", "_down"]
            for v in var_type:
                for b in bkg_files.keys():
                    for r in bins:
                        h_out = None
                        for f in bkg_files[b]:
                            input = ROOT.TFile.Open(folder + f)
                            print(input, var+"_"+r+"_"+syst+v)
                            tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_"+syst+v)))
                            tmp.Scale(lumi)
                            xbins = array('d', [500, 600, 700, 800, 1000, 1400, 2000])
                            nbin = len(xbins)-1
                            tmp = tmp.Rebin(nbin, "hist_"+b+"_"+r+"_"+syst+v, xbins)
                            if h_out == None:
                                h_out = tmp.Clone("")
                            else:
                                h_out.Add(tmp)
                            # input.Close()
                        h_out.SetName("hist_"+b+"_"+r+"_"+syst+v.replace("_", "").capitalize())
                        output.cd()
                        h_out.Write()
                for s in signal_files.keys():
                    for r in bins:
                        h_out = None
                        for f in signal_files[s]:
                            input = ROOT.TFile.Open(folder + f)
                            print(input, var+"_"+r+"_"+syst+v)
                            tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_"+syst+v)))
                            tmp.Scale(lumi)
                            xbins = array('d', [500, 600, 700, 800, 1000, 1400, 2000])
                            nbin = len(xbins)-1
                            tmp = tmp.Rebin(nbin, "hist_"+b+"_"+r+"_"+syst+v, xbins)
                            h_out = tmp.Clone("")
                            h_out.SetName("hist_"+s+"_"+r+"_"+syst+v.replace("_", "").capitalize())
                            output.cd()
                            h_out.Write()
    else:
        for b in bkg_files.keys():
            for r in bins:
                h_out = None
                for f in bkg_files[b]:
                    input = ROOT.TFile.Open(folder + f)
                    print(input, vvar+"_"+r+"_nominal")
                    tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_nominal")))
                    tmp.Scale(lumi)
                    xbins = array('d', [500, 600, 700, 800, 1000, 1400, 2000])
                    nbin = len(xbins)-1
                    tmp = tmp.Rebin(nbin, "hist_"+b+"_"+r+"_"+syst+v, xbins)
                    if h_out == None:
                        h_out = tmp.Clone("")
                    else:
                        h_out.Add(tmp)
                    # input.Close()
                h_out.SetName("hist_"+b+"_"+r+"_nominal")
                output.cd()
                h_out.Write()
        for s in signal_files.keys():
            for r in bins:
                h_out = None
                for f in signal_files[s]:
                    input = ROOT.TFile.Open(folder + f)
                    print(input, var+"_"+r+"_nominal")
                    tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_nominal")))
                    tmp.Scale(lumi)
                    xbins = array('d', [500, 600, 700, 800, 1000, 1400, 2000])
                    nbin = len(xbins)-1
                    tmp = tmp.Rebin(nbin, "hist_"+b+"_"+r+"_nominal", xbins)
                    h_out = tmp.Clone("")
                    h_out.SetName("hist_"+s+"_"+r+"_nominal")
                    output.cd()
                    h_out.Write()
    if unblind:
        h_out = None
        for r in bins:
            for f in data_files:
                input = ROOT.TFile.Open(folder + f)
                print(input, var+"_"+r+"_")
                tmp = copy.deepcopy(ROOT.TH1D(input.Get(var+"_"+r+"_")))
                if h_out == None:
                    h_out = tmp.Clone("")
                else:
                    h_out.Add(tmp)
                h_out.SetName("hist_data_obs_"+r+"_nominal")
                output.cd()
                h_out.Write()
        output.Close()
    else:
        output.Close()
        input = ROOT.TFile.Open(f"{era}/histo{era}.root")
        datahist = []
        for r in bins:
            h_out = None
            for b in jsonInput["processes"]["backgrounds"]:
                print(input, "hist_"+b+"_"+r+"_nominal")
                tmp = copy.deepcopy(ROOT.TH1D(input.Get("hist_"+b+"_"+r+"_nominal")))
                for i in range(1, tmp.GetNbinsX()+1):
                    tmp.SetBinContent(i, int(tmp.GetBinContent(i)))
                if h_out == None:
                    h_out = tmp.Clone("")
                else:
                    h_out.Add(tmp)    
            h_out.SetName("hist_data_obs_"+r+"_nominal")
            datahist.append(h_out)
        output = ROOT.TFile(f"{era}/histo{era}.root", "UPDATE")
        for h in datahist:
            output.cd()
            h.Write()
        output.Close()

def writeSingleDatacards():
    return 0

def writeTotalDatacard(jsoninput, era, unblind, sig):
    cb = ch.CombineHarvester()
    cb.SetVerbosity(3)

    cats = [(i, cat) for i,cat in enumerate(jsoninput["categories"])]
    backgrounds = jsoninput["processes"]["backgrounds"]
    # signals = jsoninput["processes"]["signals"]
    signals = [sig]

    # if unblind:
    cb.AddObservations( ["*"], ["TprimeToTZ"], ["13.6TeV"], ["jets+MET"],          cats)
    # ['*'], ['my_analysis'], ['13TeV'], ['my_category']
    cb.AddProcesses( ["*"], ["TprimeToTZ"], ["13.6TeV"], ["jets+MET"], backgrounds, cats, False)
    cb.AddProcesses( ["*"], ["TprimeToTZ"], ["13.6TeV"], ["jets+MET"], signals, cats, True)


    # Add systematics
    if opt.addSyst:
        for s in jsoninput["systematics"].keys():
            if jsoninput["systematics"][s]["processes"] == "" and jsoninput["systematics"][s]["bin"] == "":
                cb.cp().process(backgrounds+signals).AddSyst(cb, jsoninput["systematics"][s]["name"], jsoninput["systematics"][s]["type"], ch.SystMap()(jsoninput["systematics"][s]["value"]))
            elif jsoninput["systematics"][s]["processes"] == "" and jsoninput["systematics"][s]["bin"] != "":
                cb.cp().process(backgrounds+signals).bin([jsoninput["systematics"][s]["bin"]]).AddSyst(cb, jsoninput["systematics"][s]["name"], jsoninput["systematics"][s]["type"], ch.SystMap()(jsoninput["systematics"][s]["value"])) 
            elif jsoninput["systematics"][s]["processes"] != "" and jsoninput["systematics"][s]["bin"] == "":
                cb.cp().process(jsoninput["systematics"][s]["processes"]).AddSyst(cb, jsoninput["systematics"][s]["name"], jsoninput["systematics"][s]["type"], ch.SystMap()(jsoninput["systematics"][s]["value"]))
            else:
                cb.cp().process(jsoninput["systematics"][s]["processes"]).bin(jsoninput["systematics"][s]["bin"]).AddSyst(cb, jsoninput["systematics"][s]["name"], jsoninput["systematics"][s]["type"], ch.SystMap()(jsoninput["systematics"][s]["value"]))
        
        cb.ExtractShapes(f"{era}/histo{era}.root", 
                        "hist_$PROCESS_$BIN_nominal", # nominal isto saved in histo2022.root as hist_"sample"_"region"
                        "hist_$PROCESS_$BIN_$SYSTEMATIC") # syst hist_$PROCESS_$BIN_$SYSTEMATIC
    else:
        cb.ExtractShapes(f"{era}/histo{era}.root", 
                        "hist_$PROCESS_$BIN_nominal","") # nominal isto saved in histo2022.root as hist_"sample"_"region"

    cb.PrintAll()
    if not os.path.exists(era+"/"+sig):
        os.makedirs(era+"/"+sig)
    cb.WriteDatacard(era+"/"+sig+"/"+sig+".txt", era+"/"+sig+"/"+sig+".root")
    if opt.addMCStat:
        with open(era+"/"+sig+"/"+sig+".txt", "a") as f:
            f.write("* autoMCStats 0 0 1\n")

if __name__ == "__main__":  
    unblind = opt.unblind
    print("ATTENTION the UNBLIND option is set to {}".format(unblind))
    jsonInput = opt.jsonInput
    # Open JSON file
    with open(jsonInput) as file:
        print("Opening JSON file {}".format(jsonInput))
        jsoninput = json.load(file)
    if opt.inputEosFolder!="":
        print("Collecting date from {} in histo{}.root".format(opt.inputEosFolder, opt.era))
        CollectHistos(opt.inputEosFolder, jsoninput, opt.era)
    # Call the appropriate function based on the value of singledatacards
    if opt.singledatacards:
        writeSingleDatacards()
    else:
        print(jsoninput["processes"]["signals"])
        for sig in jsoninput["processes"]["signals"]:
            print(sig)
            writeTotalDatacard(jsoninput, opt.era, unblind, sig)