#light_profile.py

import numpy as np
from scipy.stats import linregress

# Use only positive PAR values for log transformation
df_valid = df_par[(df_par['PAR_smoothed'] > 0) & (df_par['Depth'] > 0)]

# Apply natural log to PAR for linear regression
ln_PAR = np.log(df_valid['PAR_smoothed'])
depth = df_valid['Depth']

# Perform linear regression: ln(PAR) = ln(I0) - Kd * z
slope, intercept, r_value, p_value, std_err = linregress(depth, ln_PAR)
Kd = -slope  # extinction coefficient is negative slope of the log-linear fit

Kd, r_value**2  # return Kd and R² to evaluate fit quality



#The estimated light extinction coefficient 
#Kd  from the smoothed PAR profile is:
#
# =1.01 /m−1
#
#with a high coefficient of determination:
#
#R 2 =0.993