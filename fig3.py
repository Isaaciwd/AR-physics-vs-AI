#%%
#%%
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.lines as mlines
import pickle
import os
darkmode = False
save = False
save_path = "/glade/work/idavis/AR_CR_project/paper_figs/fig_3.pdf"

if darkmode:
    plt.style.use('dark_background')
    colors = {
    "fourcastnet": "#F44336",    # Red
    "FourCastNet": "#F44336",    # Red
    "fourcastnetv2": "#2196F3",  # Indigo
    "FourCastNet V2": "#2196F3",  # Indigo
    "graphcast": "#AB47BC",      # Green
    "GraphCast": "#AB47BC",      # Green
    "panguweather": "#FF9800",   # Orange
    "PanguWeather": "#FF9800",   # Orange
    "tigge": "#FFFFFF",         # Purple
    "HRES": "#FFFFFF",         # Purple
    "graphcast37": "#AB47BC",    # Blue
    "aurora_ft": "#FFEB3B",       # Yellow
    "Aurora": "#FFEB3B"       # Yellow
    }
else:
    plt.style.use('default')
    # Define colors for each model
    colors = {
        "fourcastnet": "#5F559B",   # Blue
        "FourCastNet": "#5F559B",   # Blue
        "fourcastnetv2": "#0072B2", # Blue
        "FourCastNet V2": "#0072B2", # Blue
        "graphcast": "#A73C52",     # Red
        "GraphCast": "#A73C52",     # Red
        "panguweather": "#CC79A7",  # Purple
        "PanguWeather": "#CC79A7",  # Purple
        "HRES": "#000000",          # Black (keeping as requested)
        "tigge": "#FFFFFF",         # Black
        "graphcast37": "#A73C52",   # Brick red
        "aurora": "#DDAA33",        # Orange
        "aurora_ft": "#DDAA33",     # Orange
        "Aurora": "#DDAA33"         # Orange
    }


# FAR, POD, CSI
USWC = 1
landfalling = 0
threshold = 1000 # 1000 or 500 km

USWC_str = "_USWC" if USWC else ""
landfalling_str = "_landfalling" if landfalling else ""
# Load the data
gc = xr.open_dataset(f"./data/fig_3/graphcast37_metrics{USWC_str}{landfalling_str}.nc")
pw = xr.open_dataset(f"./data/fig_3/panguweather_metrics{USWC_str}{landfalling_str}.nc")
tigge = xr.open_dataset(f"./data/fig_3/tigge_metrics{USWC_str}{landfalling_str}.nc")
fc = xr.open_dataset(f"./data/fig_3/fourcastnet_metrics{USWC_str}{landfalling_str}.nc")
fcv2 = xr.open_dataset(f"./data/fig_3/fourcastnetv2_metrics{USWC_str}{landfalling_str}.nc")
aur = xr.open_dataset(f"./data/fig_3/aurora_ft_metrics{USWC_str}{landfalling_str}.nc")

# copy all of the above datasets to ./data/fig_3/
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/graphcast37_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/panguweather_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/tigge_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/fourcastnet_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/fourcastnetv2_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")
# os.system(f"cp /glade/work/idavis/AR_CR_project/rmse_data/aurora_ft_metrics{USWC_str}{landfalling_str}.nc ./data/fig_3/")  

# Prepare the data in a dictionary for easier iteration
models = {
    "HRES": tigge,
    "PanguWeather": pw,
    "GraphCast": gc,
    "FourCastNet V2": fcv2,
    "FourCastNet": fc,
    "Aurora": aur
}

# Metrics to plot
metrics = ["CSI", "POD", "FAR"]

# Create a figure for each metric
figs, axs = plt.subplots(3, 1, figsize=(10, 15))

# Iterate through each metric and plot for each model
for i, metric in enumerate(metrics):
    # Create a list to hold custom legend entries
    custom_legend_entries = []
    
    for model_name, model_data in models.items():
        # Plot the actual data
        x = model_data["time"] * 6 / 24  # convert from steps to days
        if model_name == "HRES":
            axs[i].plot(x, model_data[f"{metric}_{threshold}"], 
                       color=colors[model_name], 
                       linestyle='--',
                       linewidth=3)
        else:
            axs[i].plot(x, model_data[f"{metric}_{threshold}"], 
                       color=colors[model_name], 
                       linestyle='-')
        
        std_error = model_data[f"{metric}_{threshold}"].attrs["std"] / np.sqrt(model_data[f"{metric}_{threshold}"].attrs["count"])
        axs[i].fill_between(x, model_data[f"{metric}_{threshold}"] - std_error, 
                           model_data[f"{metric}_{threshold}"] + std_error, 
                           color=colors[model_name], 
                           alpha=0.3)
        
        # Add a custom legend entry for each model
        custom_legend_entries.append(mlines.Line2D([], [], color=colors[model_name], label=model_name))

        print("model_name: ", model_name)
    
    # # Add custom legend entries for the 1000 km and 500 km thresholds
    # custom_legend_entries.append(mlines.Line2D([], [], color='black', linestyle='-', label='1000 km'))
    # custom_legend_entries.append(mlines.Line2D([], [], color='black', linestyle='--', label='500 km'))

    # Add labels and title with larger font sizes
    axs[i].set_title(f"{USWC_str[1:]} {landfalling_str[1:]} {metric} vs Forecast Lead Time, {threshold} km threshold", fontsize=20)
    axs[i].set_ylabel(f"{metric} Value", fontsize=18)
    # axs[i].set_ylim(-0.2,1.2)
    axs[i].set_ylim(0,1)
    axs[i].tick_params(axis='both', which='major', labelsize=20)

    axs[i].grid(True, linestyle='--', alpha=0.6) # Add light dashed grid lines

    axs[i].set_xlim(0.25, 10)  # Set x-axis limits to 0-10 days


# Hide x-axis labels for all but the bottom plot
for ax in axs[:-1]:
    ax.set_xticklabels([])

# Add x-axis label to the bottom plot
axs[-1].set_xlabel("Forecast Lead Time (days)", fontsize=18)

# Increase the font size of the x and y tick labels
for ax in axs:
    ax.tick_params(axis='both', which='major', labelsize=20)

# Add legend with larger font size
axs[0].legend(handles=custom_legend_entries, fontsize=16)

plt.suptitle("CSI, POD, and FAR vs. Leadtime", y=0.985,fontsize=20+3, fontweight='bold')

plt.tight_layout()
if save:
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()
