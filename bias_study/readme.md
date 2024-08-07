# Bias study
Thise code implemnt the bias study for $W \to\tau(3\mu)\nu$.

## Evaluate bias with significance
We take the exponential modela as reference to compute the fit bias.
First make sure to have a datacard and workspace for each category with exponential fit and generate toys
```
text2workspace.py input_combine/datacard_WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940.txt
python3 AdaRunBiasInSignificance.py --input_datacard input_combine/datacard_WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940.root --tag WTau3Mu_A22_LxyS2.1_2024Jul11_expo_bdt0.9940 --nToys 50000 --mode generate --gen_func expo
```
