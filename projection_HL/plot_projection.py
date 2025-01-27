import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath('../'))
from style.color_text import color_text as ct



lumi_Run2 = 90.4 # fb-1
lumi_HL1 = 2000 # fb-1
lumi_HL2 = 3000 # fb-1
lumi_points = [lumi_Run2, lumi_HL1, lumi_HL2]   # fb-1

limit_Run2 = 40.6 # 1e-9
limit_HL1 = 3.6
limit_HL1b = 6.6
limit_HL2 = 2.6
limit_HL2b = 5.2

# store in dataframes
df_A = pd.DataFrame({
    'lumi'   : lumi_points, 
    'limit'  : [limit_Run2, limit_HL1, limit_HL2],
    '-1sigma': [limit_Run2,  2.0, 1.5],
    '+1sigma': [limit_Run2,  6.4, 4.7],
    '-2sigma': [limit_Run2,  1.3, 0.9],
    '+2sigma': [limit_Run2, 10.5, 7.7],
})

df_B = pd.DataFrame({
    'lumi'   : lumi_points, 
    'limit'  : [limit_Run2, limit_HL1b, limit_HL2b],
    '-1sigma': [limit_Run2,  4.4, 3.5],
    '+1sigma': [limit_Run2, 10.1, 8.0],
    '-2sigma': [limit_Run2,  3.1, 2.5],
    '+2sigma': [limit_Run2, 15.1, 11.8],
})
df_HN = pd.DataFrame({
    'lumi'   : lumi_points, 
    'limit'  : [limit_Run2, 0.3, 0.2],
    '-1sigma': [limit_Run2, 0.2, 0.1],
    '+1sigma': [limit_Run2, 0.4, 0.3],
    '-2sigma': [limit_Run2, 0.1, 0.1],
    '+2sigma': [limit_Run2, 0.5, 0.4],
})

x_lumi = np.linspace(80, 3000, 100)
y_limit = limit_Run2 * np.sqrt(lumi_Run2/x_lumi)
y_linear = limit_Run2 * lumi_Run2/x_lumi

# compare scenarios
plt.figure(figsize=(8, 6))

plt.plot(x_lumi, y_limit, '--' , c = 'r',label=r'$\propto \sqrt{L}$')
plt.plot(x_lumi, y_linear, '-', c = 'r',label=r'$\propto L$')
plt.errorbar(df_A['lumi'], df_A['limit'], yerr=[df_A['limit']-df_A['-1sigma'], df_A['+1sigma']-df_A['limit']], fmt='o', c = 'k', label=r'Asymptotic (A) $\pm 1\sigma$')
plt.errorbar(df_B['lumi'], df_B['limit'], yerr=[df_B['limit']-df_B['-2sigma'], df_B['+2sigma']-df_B['limit']], fmt='o', c = 'b', label=r'Asymptotic (B) $\pm 1\sigma$')
plt.xlabel('Int. luminosity [fb$^{-1}$]', fontsize=14)
plt.ylabel(r'90% CL limit BR$(\tau \rightarrow 3\mu) \times 10^{-9}$ [pb]', fontsize=14)
plt.legend(fontsize=16, loc='upper right', borderpad=0.5)
plt.grid()
plt.title('HL-LHC projection (W channel)') 
plt.savefig('HL-LHC_projection_AvsB.png')



# plot the projection - with bands
plt.figure(figsize=(8, 6))
x_lumi = np.linspace(80, 3000, 100)
y_limit = 40.6 * np.sqrt(lumi_Run2/x_lumi)
y_linear = 40.6 * lumi_Run2/x_lumi
plt.fill_between(df_A['lumi'], df_A['-2sigma'], df_A['+2sigma'], color=ct.CMS_yellow)
plt.fill_between(df_A['lumi'], df_A['-1sigma'], df_A['+1sigma'], color=ct.CMS_green)
plt.plot(df_A['lumi'], df_A['limit'], '--o', c = 'k', label='Asymptotic (A)')
plt.plot(x_lumi, y_limit, '--' , c = 'b',label=r'$\propto \sqrt{L}$')
plt.plot(x_lumi, y_linear, '-', c = 'b',label=r'$\propto L$')
plt.xlabel('Int. luminosity [fb$^{-1}$]', fontsize=14)
plt.ylabel(r'90% CL limit BR$(\tau \rightarrow 3\mu) \times 10^{-9}$ [pb]', fontsize=14)
plt.legend(fontsize=16)
plt.grid()
plt.title('HL-LHC projection (W channel)')  
plt.savefig('HL-LHC_projection_bands_A.png')

