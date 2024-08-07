# WTau3Mu_limits

## Installation

To use this code, you need to have `CMSSW_14_1_0_pre4` and CombineV10 installed. Follow the instructions below to set up the environment:
### Get Combine v10
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
### Get this repository
Clone this repository and compile with:
```
cd CMSSW_14_1_0_pre4/src/
git clone git@github.com:BasChiara/WTau3Mu_limits.git
cd WTau3Mu_limits
scram b
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
