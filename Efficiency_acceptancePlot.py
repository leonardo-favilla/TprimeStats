import ROOT
from array import array
import cmsstyle as CMS
from samples import *
ROOT.gROOT.SetBatch()

regions = ["MixSR0fjets", "MixSRatleast1fjets", "MerSR0fjets", "MerSRatleast1fjets"]

masses      = [0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]
# masses      = [1.6, 1.7, 1.8]
sigma       = {str(m) : sample_dict["TprimeToTZ_"+str(int(m*10**3))+"_2022"].sigma*10**3 for m in masses}
lumi        = 34.54

def getEfficiencyAcceptance(mass=0.7, sigma=sigma["1.7"], lumi=34.54):
    final_rate = {}
    f = open("./2022tot/TprimeToTZ_"+str(int(mass*10**3))+"/TprimeToTZ_"+str(int(mass*10**3))+".txt")
    rates_line = f.readlines()[19].split()
    rates = rates_line[-8:-4]
    final_rate ={
        "MixSR0fjets"        : float(rates[0])/(sigma*lumi),     
        "MixSRatleast1fjets" : float(rates[1])/(sigma*lumi), 
        "MerSR0fjets"        : float(rates[2])/(sigma*lumi),     
        "MerSRatleast1fjets" : float(rates[3])/(sigma*lumi)
    } 
    print(mass, final_rate)
    f.close()
    return final_rate
eff_tot     = {str(m): getEfficiencyAcceptance(m, sigma[str(m)], lumi) for m in masses}

print([eff_tot[str(m)][regions[0]] for m in masses])

eff = {r: [eff_tot[str(m)][r]*100 for m in masses] for r in regions}

plot_eff = {r: ROOT.TGraph(len(masses), array('d', masses), array('d', eff[r])) for r in regions}

# r = regions[0]
for r in regions:
    CMS.SetExtraText("Preliminary")
    iPos = 0
    canv_name = 'efficiency_acceptance_'+r
    CMS.SetLumi("34.54")

    CMS.SetEnergy("13.6")
    CMS.ResetAdditionalInfo()
    y_str = "Acceptance #times Efficiency (%)"
    y = eff[r]
    canv = CMS.cmsCanvas(canv_name, min(masses)-0.05,max(masses)+0.05, 0, 1,"T' mass[TeV]",y_str,square=CMS.kSquare,extraSpace=0.05,iPos=iPos)
    CMS.cmsDraw(plot_eff[r], "P", mcolor=ROOT.TColor.GetColor("#bd1f01"))

    # canv.SetLogy()
    leg = CMS.cmsLeg(0.5, 0.90 - 0.05 * 4, 0.95, 0.90, textSize=0.04)
    leg.AddEntry(plot_eff[r], "#Gamma/m_{T}<0.01","AP")
    CMS.SaveCanvas(canv, "./EfficiencyAcceptancePlot"+r+".png", False)
    CMS.SaveCanvas(canv, "./EfficiencyAcceptancePlot"+r+".pdf")