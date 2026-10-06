import subprocess
import os
import optparse
import json

usage = "python3 doGoodnessOfFit.py"
parser = optparse.OptionParser(usage)
parser.add_option("-e", "--era",       dest="era",       type=str, default="2022",          help="Era of the datacard")
parser.add_option("-m", "--massPoint", dest="massPoint", type=int, default=700,             help="Tprime mass point")
parser.add_option("-j", "--jsonInput", dest="jsonInput",           default="settings.json", help="Settings JSON file")
parser.add_option("-t", "--toys",      dest="toys",      type=int, default=1000,            help="Number of toys")
parser.add_option("-s", "--seed",      dest="seed",      type=int, default=123456,          help="Random seed")
(opt, args) = parser.parse_args()

with open(opt.jsonInput) as file:
    jsoninput = json.load(file)

era                 = opt.era
mass                = str(opt.massPoint)
toys                = str(opt.toys)
seed                = str(opt.seed)
dc_folder           = jsoninput["dc-folder"][era]
gof_dir             = f"{dc_folder}/TprimeToTZ_{mass}/gof/"
data_output         = f"higgsCombine_gof_data_bonly.GoodnessOfFit.mH125.root"
toys_output         = f"higgsCombine_gof_toys_bonly.GoodnessOfFit.mH125.{seed}.root"
# data_gof_options    = "--algo saturated --setParameters r=0 --freezeParameters r"
# mc_gof_options      = "--algo saturated --setParameters r=0 --freezeParameters r --toysFrequentist"
data_gof_options    = "--algo saturated --toysFrequentist --bypassFrequentistFit  --rMin -250 --rMax 250"
mc_gof_options      = "--algo saturated --toysFrequentist --bypassFrequentistFit  --rMin -250 --rMax 250"

print(f"Running background-only Goodness of Fit for era {era}, mass {mass}, toys {toys}")
if not os.path.exists(gof_dir):
    os.makedirs(gof_dir)


subprocess.run(f"text2workspace.py ../TprimeToTZ_{mass}.txt -m 125 -o workspace_TprimeToTZ_{mass}.root",                                             shell=True, check=True, cwd=gof_dir)
subprocess.run(f"combine -M GoodnessOfFit -d workspace_TprimeToTZ_{mass}.root -m 125 {data_gof_options} -n _gof_data_bonly",                         shell=True, check=True, cwd=gof_dir)
subprocess.run(f"combine -M GoodnessOfFit -d workspace_TprimeToTZ_{mass}.root -m 125 {mc_gof_options} -n _gof_toys_bonly -t {toys} -s {seed}",       shell=True, check=True, cwd=gof_dir)
subprocess.run(f"combineTool.py -M CollectGoodnessOfFit --input {data_output} {toys_output} -m 125.0 -o gof.json",                                   shell=True, check=True, cwd=gof_dir)
subprocess.run(f"python3 plotGoodnessOfFit.py -i {gof_dir}/gof.json -e {era} -j {opt.jsonInput} -m {mass}",                                          shell=True, check=True, cwd=".")