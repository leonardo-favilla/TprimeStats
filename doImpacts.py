import subprocess
import os
import optparse

usage = 'python3 doImpacts.py'
parser = optparse.OptionParser(usage)
parser.add_option('--era', dest='era', type=str, default = '2022', help='Please enter the era of the datacard, if not specified the code will take the era 2022')
parser.add_option('-m', '--massPoint', type=int, default = 700, help='Please enter the mass point of the datacard, if not specified the code will take the mass point 700')
parser.add_option('--FitOption', dest='FitOption', type=str, default = "-t -1 --setParameterRanges r=-100,100", help='Please enter the fit option, if not specified the code will take the fit option -t -1')
(opt, args) = parser.parse_args()

era = opt.era
mass = str(opt.massPoint)
FitOption = opt.FitOption

print("Running impacts for era: {}, mass: {}, FitOption: {}".format(era, mass, FitOption))

if not os.path.exists("{}/TprimeToTZ_{}/impacts/".format(era, mass)):
    os.makedirs("{}/TprimeToTZ_{}/impacts/".format(era, mass))
# subprocess.run("pwd")
# Change working directory for subsequent commands by using cwd parameter in subprocess.run
impact_dir = "{}/TprimeToTZ_{}/impacts/".format(era, mass)

subprocess.run("text2workspace.py ../TprimeToTZ_{}.txt -m 125".format(mass), shell=True, check=True, cwd=impact_dir)
subprocess.run("combineTool.py -M Impacts -d ../TprimeToTZ_{}.root -m 125 --doInitialFit {}".format(mass, FitOption), shell=True, check=True, cwd=impact_dir)
subprocess.run("combineTool.py -M Impacts -d ../TprimeToTZ_{}.root -m 125 --doFit {} --parallel 10".format(mass, FitOption), shell=True, check=True, cwd=impact_dir)
subprocess.run("combineTool.py -M Impacts -d ../TprimeToTZ_{}.root -m 125 -o impact.json".format(mass), shell=True, check=True, cwd=impact_dir)   
subprocess.run("plotImpacts.py -i impact.json -o impacts", shell=True, check=True, cwd=impact_dir)