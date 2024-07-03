# WTau3Mu_limits

**INSTALL COMBINE v10**
letest version of Combine working on el9
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
and CombineHarvester package
```
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b
```
**DOWNLOAD THIS REPO FOR Wtau3mu LIMITS**
```
git clone git@github.com:BasChiara/WTau3Mu_limits.git WTau3Mu_limits
cd WTau3Mu_limits
```
**RUN MVA SELECTION OPTIMIZATION**\
You can run the optimization over the 3 categories in parallel using HTCondor. Use the script `scripts/to_submit_BDToptim.sh` which calls `scripts/submitBDTopt_onCondor.py`, modify the tag and the I/O directories before using it.

**BIAS STUDY (~Hggtautau approach)**\
In `bias_study` folder there are some scripts to produce bias test 
