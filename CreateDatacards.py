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
import sys

usage = 'python3 CreateDatacards.py -e 2023 -j settings.json --addSyst --addMCStat'
parser = optparse.OptionParser(usage)
parser.add_option('-e', '--era',                dest='era',             type=str,               default="2022",             help='insert era (e.g. 2022, 2022EE)')
parser.add_option('-j', '--jsonInput',          dest='jsonInput',       type=str,               default="settings.json",    help='json file containing the settings')
parser.add_option('-u', '--unblind',            dest='unblind',         action='store_true',    default=False,              help='Unblind')
# parser.add_option('-s', '--singledatacards',    dest='singledatacards', action='store_true',    default=False,              help='Write single datacards per each bin')
parser.add_option('--addSyst',                  dest='addSyst',         action='store_true',    default=False,              help='add Systematics in the datacards')
parser.add_option('--addMCStat',                dest='addMCStat',       action='store_true',    default=False,              help='add auto MC Stat in the datacards')
# parser.add_option('-l', '--lumi', dest='lumi', type=str, default="1", help='luminosity, default 1')
(opt, args)     = parser.parse_args()
# Open JSON file
with open(opt.jsonInput) as file:
    print("Opening JSON file {}".format(opt.jsonInput))
    jsoninput   = json.load(file)
lumi_dict                           = jsoninput["lumi_dict"]
lumi_dict["2022+2023"]              = lumi_dict["2022"] + lumi_dict["2023"]
lumi_dict["2022+2023+2024"]         = lumi_dict["2022"] + lumi_dict["2023"] + lumi_dict["2024"]


era             = opt.era
# lumi            = lumi_dict[era]
unblind         = opt.unblind
# inputEosFolder  = jsoninput["plots-folder"][era]
outFolderPath   = jsoninput["dc-folder"][era]

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
        print("Systematics to be added: ", jsoninput["systematics"].keys())
        for s in jsoninput["systematics"].keys():
            name        = jsoninput["systematics"][s]["name"]
            processes   = jsoninput["systematics"][s]["processes"]
            bins        = jsoninput["systematics"][s]["bin"]
            type        = jsoninput["systematics"][s]["type"]
            syst_value  = jsoninput["systematics"][s]["value"]
            if isinstance(syst_value, dict):
                value = syst_value[era]
            else:
                value = syst_value

            if processes == "" and bins == "":
                cb.cp().process(backgrounds+signals).AddSyst(cb, name, type, ch.SystMap()(value))
            elif processes == "" and bins != "":
                cb.cp().process(backgrounds+signals).bin([bins]).AddSyst(cb, name, type, ch.SystMap()(value))
            elif processes != "" and bins == "":
                cb.cp().process(processes).AddSyst(cb, name, type, ch.SystMap()(value))
            else:
                cb.cp().process(processes).bin(bins).AddSyst(cb, name, type, ch.SystMap()(value))

        cb.ExtractShapes(f"{outFolderPath}/histo{era}.root",
                        "hist_$PROCESS_$BIN_nominal", # nominal isto saved in histo2022.root as hist_"sample"_"region"
                        "hist_$PROCESS_$BIN_$SYSTEMATIC") # syst hist_$PROCESS_$BIN_$SYSTEMATIC
    else:
        cb.ExtractShapes(f"{outFolderPath}/histo{era}.root",
                        "hist_$PROCESS_$BIN_nominal","") # nominal isto saved in histo2022.root as hist_"sample"_"region"

    cb.PrintAll()
    if not os.path.exists(f"{outFolderPath}/{sig}"):
        os.makedirs(f"{outFolderPath}/{sig}")
    cb.WriteDatacard(f"{outFolderPath}/{sig}/{sig}.txt", f"{outFolderPath}/{sig}/{sig}.root")
    if opt.addMCStat:
        with open(f"{outFolderPath}/{sig}/{sig}.txt", "a") as f:
            f.write("* autoMCStats 0 0 1\n")

if __name__ == "__main__":
    # print("ATTENTION the UNBLIND option is set to {}".format(unblind))
    # if inputEosFolder!="":
    #     print("Collecting data from {} in histo{}.root".format(inputEosFolder, era))
    #     CollectHistos(inputEosFolder, outFolderPath, jsoninput, era)
    # Call the appropriate function based on the value of singledatacards
    # if opt.singledatacards:
    #     writeSingleDatacards()
    # else:
    #     print(jsoninput["processes"]["signals"])
    #     for sig in jsoninput["processes"]["signals"]:
    #         print(sig)
    #         writeTotalDatacard(jsoninput, era, unblind, sig)

    print(jsoninput["processes"]["signals"])
    for sig in jsoninput["processes"]["signals"]:
        print(sig)
        writeTotalDatacard(jsoninput, era, unblind, sig)