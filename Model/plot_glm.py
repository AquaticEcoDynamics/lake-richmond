import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from glmpy import plots

nc = plots.NCPlotter("richmond/output/output.nc")

vars = nc.get_profile_vars()

plot_vars = vars[3:7]     # returns the variables: ['salt', 'temp', 'dens', 'radn']
fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 14))
for idx, var, in enumerate(plot_vars):
    out = nc.plot_var_profile(axs[idx], var)
    long_name = nc.get_long_name(var)
    units = nc.get_units(var)
    col_bar = fig.colorbar(out)
    col_bar.set_label(f"{long_name} ({units})")

plt.savefig('lake_4.png')


lake = plots.LakePlotter("richmond/output/lake.csv")

fig, ax = plt.subplots(figsize=(10, 5))
out = lake.water_balance_components(
    ax=ax, 
    rain_params={"linestyle": "--"},
    local_runoff_params=None, 
    overflow_vol_params=None,
    snowfall_params=None
)
ax.legend(handles=out)

plt.savefig('lake_wb.png')


fig, ax = plt.subplots(figsize=(10, 5))
lake.lake_level(ax=ax)
plt.savefig('lake_level.png')
