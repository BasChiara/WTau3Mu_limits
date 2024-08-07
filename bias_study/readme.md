# Bias study
Thise code implement the bias study for $W \to\tau(3\mu)\nu$.

## Evaluate bias with significance (B only)
We take the exponential modela as reference to compute the fit bias.
First make sure to have a datacard and workspace for each category with exponential fit and generate toys
```
text2workspace.py input_combine/datacard_WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940.txt
python3 AdaRunBiasInSignificance.py --input_datacard input_combine/datacard_WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940.root --tag WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940 --nToys 50000 --mode generate --gen_func expo
```
## Evaluate bias with signal strenght (S+B)
Generate toys with a given bkg model and injecting signal by acting on the POI value ($r$). Then fit each toy with S+B model where the B model can be either the one used for toy generation, either a different one. Finally plot the pull of the signal strength, $(r_{gen}-r_{fit})/\sigma_{fit}$, and extract the bias from the mean of the distribution.\
Before starting create the needed directories and make sure you have the compiled datacard both for generating and fitting
```
mkdir input_combine
mkdir toys
mkdir plots
```
The full procedure is embedded in the script `to_run_biasSignal.py`, just need to activate the step to run by setting the following variables inside it.
```
do_gen_step     = True
do_fit_step     = True
do_pull_step    = True
```
