# WTau3Mu_limits

## Installation

To use this code, you need to have `CMSSW_14_1_0_pre4` and CombineV10 installed. Follow the instructions below to set up the environment:
### Dependencies : install Combine v10
To get the letest version of Combine working on el9 run
```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
```
```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.0.1
scramv1 b clean; scramv1 b # always make a clean build
```
Also download CombineHarvester package running
```
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b
```
### Clone this repository
Clone this repository and compile with:
```
cd CMSSW_14_1_0_pre4/src/
git clone git@github.com:BasChiara/WTau3Mu_limits.git
cd WTau3Mu_limits
scram b
```
## Run limits
Create a working directory and store your datacard in a sub-directoy named `input_combine`, workspaces can be stored in any location, just make sure the 
datacard is correctly linked to the workspaces.
```
mkdir -p work_dir/input_combine
cp datacard.txt work_dir/input_combine 
```
You can calculate limits in asymptotic approximation or using toys.
### AsymptoticLimits
Run the script `models/run_limitFromDatacard.py` with the following options
```
python3 models/run_limitFromDatacard.py --input_datacard work_dir/input_combine/datacard.txt -w ./work_dir -n [name for combine output] -s all -M AsymptoticLimits --CL [confidence_level]
```

### HybridNew
Run the script `models/run_limitFromDatacard.py` with the following options
```
python3 models/run_limitFromDatacard.py --input_datacard work_dir/input_combine/datacard.txt -w ./work_dir -n [name for combine output] -s all -M HybridNew -T [number of toys] --CL [confidence_level] -q [quantile]
```

## Submit limits on Condor
Run the script `scripts/submit_limits_onCondor.py`.\
Using AsymptoticLimits
```
python3 scripts/submit_limits_onCondor.py --input_datacard work_dir/input_combine/datacard.txt --workdir ./work_dir -M AsymptoticLimits --tag [name for combine output] --category ABC --year [year]
```
or using HybridNew
```
python3 scripts/submit_limits_onCondor.py --input_datacard work_dir/input_combine/datacard.txt --workdir ./work_dir -M HybridNew --nToys [number of toys] --tag [name for combine output] --category ABC --year [year] -r 24 --quantile [nominal, 1sigma, 2sigma or all]
```

## BDT working point
Optimize the analysis working point, given a BDT model, provide fits in ROOT v26/xx first. 
Modify with the correct tags the script `scripts/to_submit_BDToptim.sh` and lounch it.
```
./scripts/to_submit_BDToptim.sh
```
**RUN MVA SELECTION OPTIMIZATION**\
You can run the optimization over the 3 categories in parallel using HTCondor. Use the script `scripts/to_submit_BDToptim.sh` which calls `scripts/submitBDTopt_onCondor.py`, modify the tag and the I/O directories before using it.

**BIAS STUDY (~Hggtautau approach)**\
In `bias_study` folder there are some scripts to produce bias test 
