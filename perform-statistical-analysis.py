import subprocess
import json
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-e', '--era',          type=str,               default='2023',             help='Era of the datacard')
parser.add_argument('-j', '--jsonInput',    type=str,               default='settings.json',    help='Settings JSON file')
parser.add_argument("-u", "--unblind",      action="store_true",                                help="Use data instead of the background sum")
args = parser.parse_args()

era             = args.era
settings_file   = args.jsonInput
unblind         = args.unblind

with open(settings_file) as file:
    print("Opening JSON file {}".format(settings_file))
    jsoninput   = json.load(file)


output_dir      = jsoninput["dc-folder"][era]
massPoints      = [signal.split('_')[-1] for signal in jsoninput["processes"]["signals"]]


cmd1 = f"python3 CollectHistos.py -e {era} -j {settings_file} --addSyst {'--unblind' if unblind else ''}"
cmd2 = f"python3 CreateDatacards.py -e {era} -j {settings_file} --addSyst"
subprocess.run(cmd1, shell=True, check=True)
subprocess.run(cmd2, shell=True, check=True)

for mass in massPoints:
    cmd3 = f"python3 doImpacts.py -e {era} -m {mass} -j {settings_file}"
    subprocess.run(cmd3, shell=True, check=True)