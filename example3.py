import CombineHarvester.CombineTools.ch as ch

cb = ch.CombineHarvester()
cb.SetVerbosity(3)

cats = [(0, "SRTop"), (1, "AH"), (2, "SL"), (3, "AH1lWR"), (4, "AH0lZR")]
processes = ["WJets", "ZJets", "TT", "QCD"]

# cb.AddObservations( ["*"], ["*"], ["*"], ["*"],          cats)
cb.AddProcesses(    ["*"], ["*"], ["*"], ["*"], processes, cats, False)

cb.ExtractShapes("histo2022.root", 
                 "hist_$PROCESS_$BIN", # nominal isto saved in histo2022.root as hist_"sample"_"region"
                 "") # syst hist_$PROCESS_$BIN_$SYSTEMATIC


cb.PrintAll()
cb.WriteDatacard("example3.txt", "example3.root")