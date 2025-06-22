import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from glmpy import plots

#----------------------------------------------
# Lake GLM profile series

nc = plots.NCPlotter("richmond/output/output.nc")
vars = nc.get_profile_vars()

plot_vars = vars[3:6]     # returns the variables: ['salt', 'temp', 'dens', 'radn']
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 14))
for idx, var, in enumerate(plot_vars):
    out = nc.plot_var_profile(axs[idx], var)
    long_name = nc.get_long_name(var)
    units = nc.get_units(var)
    col_bar = fig.colorbar(out)
    col_bar.set_label(f"{long_name} ({units})")

plt.savefig('lake_3panel_glm.png')

#----------------------------------------------
# Lake WATER BALANCE plots

lake = plots.LakePlotter("richmond/output/lake.csv")

fig, axs = plt.subplots(nrows=3, ncols=1,figsize=(10, 15))
out1 = lake.water_balance_components(
    ax=axs[0], 
    rain_params={"linestyle": "--","linewidth": 0.5},
    evaporation_params={"linewidth": 0.5},
    local_runoff_params={"linestyle": "-.","linewidth": 0.5}, 
    overflow_vol_params={"linestyle": "dotted"},
    snowfall_params=None
)
axs[0].set_xlim(pd.Timestamp("2010-01-01"), pd.Timestamp("2016-01-01")) 
# Second y-axis
ax2 = axs[0].twinx()
outl = lake.lake_level(ax=ax2)
ax2.legend(handles=outl,  loc='upper right')
ax2.set_ylim(-2.5, 2)
ax2.set_yticks([-0.5, 0, 0.5, 1, 1.5]) 
ax2.axvspan(pd.Timestamp("2011-01-01"), pd.Timestamp("2012-01-01"), color='yellow', alpha=0.1)
ax2.axvspan(pd.Timestamp("2013-01-01"), pd.Timestamp("2014-01-01"), color='gray', alpha=0.1)
ax2.axvspan(pd.Timestamp("2015-01-01"), pd.Timestamp("2016-01-01"), color='gray', alpha=0.1)

out2 = lake.water_balance_components(
    ax=axs[1], 
    rain_params={"linestyle": "--","linewidth": 0.5},
    evaporation_params={"linewidth": 0.5},
    local_runoff_params={"linestyle": "-.","linewidth": 0.5}, 
    overflow_vol_params={"linestyle": "dotted"},
    snowfall_params=None
)
axs[1].set_ylim(-10000, 15000)
axs[1].set_xlim(pd.Timestamp("2010-01-01"), pd.Timestamp("2016-01-01")) 
axs[1].axvspan(pd.Timestamp("2011-01-01"), pd.Timestamp("2012-01-01"), color='yellow', alpha=0.1)
axs[1].axvspan(pd.Timestamp("2013-01-01"), pd.Timestamp("2014-01-01"), color='gray', alpha=0.1)
axs[1].axvspan(pd.Timestamp("2015-01-01"), pd.Timestamp("2016-01-01"), color='gray', alpha=0.1)

out3 = lake.water_balance_components(
    ax=axs[2], 
    rain_params={"linestyle": "--", "linewidth": 0.5},
    evaporation_params={"linewidth": 0.5},
    local_runoff_params={"linestyle": "-."}, 
    overflow_vol_params={"linestyle": "dotted"},
    snowfall_params=None
)
axs[2].set_ylim(-6000, 15000)
axs[2].set_xlim(pd.Timestamp("2011-01-01"), pd.Timestamp("2012-01-01")) 
axs[2].legend(handles=out1,loc='upper left')

plt.savefig('lake_water_balance.png')

#----------------------------------------------
# Lake WATER LEVEL plots

fig, ax = plt.subplots(figsize=(10, 5))
lake.lake_level(ax=ax)
plt.savefig('lake_level.png')


#----------------------------------------------
# Lake AED profile series

#vars = nc.get_profile_vars()
#print("Current vars:", vars)
plot_vars = [vars[11], vars[13], vars[14]]   # returns the AED variables

fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 14))
for idx, var, in enumerate(plot_vars):
    out = nc.plot_var_profile(axs[idx], var)
    long_name = nc.get_long_name(var)
    units = nc.get_units(var)
    col_bar = fig.colorbar(out)
    col_bar.set_label(f"{long_name} ({units})")

plt.savefig('lake_3panel_aed.png')