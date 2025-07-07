#%%
import numpy as np
import os
import xarray as xr
import matplotlib.pyplot as plt
import pickle

darkmode= False
variables = ["TMQ", "PSL", "WIND850", "TMQ_bias"]  # Changed U850 to WIND850 # This line is now commented out
# variables = ["TMQ", "PSL", "U850", "V850"]  # To recreate the original plot with U850 and V850
save = False
save_path = "/glade/work/idavis/AR_CR_project/paper_figs/fig_1.pdf"
# Define colors for each line'
if darkmode:
    colors = {
        "fourcastnet": "#F44336",
        "fourcastnetv2": "#2196F3", 
        "graphcast": "#4CAF50",
        "panguweather": "#FF9800",
        "HRES": "#FFFFFF",
        "graphcast37": "#AB47BC",
        "aurora": "#FFEB3B"
    }
    # Set plotting parameters
    plt.style.use('dark_background')
else:
    # colors = {
    #     "fourcastnet": "#F44336",  # Red
    #     "fourcastnetv2": "#3F51B5",  # Indigo
    #     "graphcast": "#4CAF50",  # Green
    #     "panguweather": "#FF9800",  # Orange
    #     "HRES": "#000000",  # Black
    #     "graphcast37": "#9C27B0",  # Blue
    #     "aurora":   "#FFEB3B"# Dark Yellow (Dark Goldenrod)
    #     # "aurora":   "#2196F3"# Dark Yellow (Dark Goldenrod)
    # }
    colors = {
        "fourcastnet": "#5F559B",   # Blue
        "fourcastnetv2": "#0072B2", # Orange
        "graphcast": "#009E73",     # Teal
        "panguweather": "#CC79A7",  # Purple
        "HRES": "#000000",          # Black (keeping as requested)
        "graphcast37": "#A73C52",   # Brick red (replacing hard-to-see yellow)
        "aurora": "#DDAA33"         # Purple-blue (replacing similar blue)
    }
# Set plotting parameters
font_multiplier = 1.25
plt.rcParams['font.size'] = 17 * font_multiplier
plt.rcParams['axes.labelsize'] = 18 * font_multiplier
plt.rcParams['axes.titlesize'] = 18 * font_multiplier
plt.rcParams['xtick.labelsize'] = 18 * font_multiplier
plt.rcParams['ytick.labelsize'] = 18 * font_multiplier
plt.rcParams['legend.fontsize'] = 18 #* font_multiplier
plt.rcParams['figure.titlesize'] = 15 * font_multiplier

# Create figure with 2x2 subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
x2 = (np.arange(0, 41)) * 0.25  # Convert 6-hour intervals to days (6/24 = 0.25)
cap_size = 5
for i, var in enumerate(variables):
    row = i // 2
    col = i % 2
    ax = axs[row, col]
    
    if var == "TMQ_bias":
        filename = f"./data/fig_1/{var[:3]}_bias.pickle"
        # os.system(f"cp {filename} /glade/work/idavis/AR_CR_project/minimally_reproducable_figs/data/fig_1/{var[:3]}_bias.pickle")

    else:
        filename = f"./data/fig_1/{var}_RMSE.pickle"
        # os.system(f"cp {filename} /glade/work/idavis/AR_CR_project/minimally_reproducable_figs/data/fig_1/{var}_RMSE.pickle")

    try:
        with open(filename, 'rb') as handle:
            PICKLE_DATA = pickle.load(handle)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found. Skipping variable '{var}'.")
        ax.text(0.5, 0.5, f"Data not found for\\n{var}", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(f"{var} (Data Missing)")
        if row == 1: ax.set_xlabel('Lead Time (Days)')
        else: ax.set_xticklabels([])
        ax.set_xticks(np.arange(0, 10.1, 1))
        ax.grid(True, linestyle='--', alpha=0.6)
        if i == 0: ax.legend() # Still add legend to first panel even if data is missing for it
        continue # Skip to the next variable
    models_to_plot = ["fourcastnet", "fourcastnetv2", "panguweather", "tigge", "graphcast37", "aurora"]
    plotted_means = {}
    plotted_sems = {}

    for model_key in models_to_plot:
        if model_key not in PICKLE_DATA:
            print(f"Warning: Model key '{model_key}' not found in {filename} for variable '{var}'. Plotting NaNs for this model.")
            plotted_means[model_key] = np.full_like(x2, np.nan)
            plotted_sems[model_key] = np.full_like(x2, np.nan)
            continue

        data = PICKLE_DATA[model_key]
        plotted_means[model_key] = np.nanmean(data, axis=0)
        data_std = np.nanstd(data, axis=0)
        n_samples = np.sum(~np.isnan(data), axis=0) # Count non-NaN samples for each lead time
        
        # Calculate SEM, avoid division by zero or sqrt of zero if n_samples is 0
        plotted_sems[model_key] = np.zeros_like(data_std, dtype=float) # Initialize with zeros
        valid_samples_mask = n_samples > 0
        plotted_sems[model_key][valid_samples_mask] = data_std[valid_samples_mask] / np.sqrt(n_samples[valid_samples_mask])

    # Plot lines
    # Using .get() with a default NaN array for robustness if a key was still missed (though handled above)
    ax.plot(x2, plotted_means.get("fourcastnet", np.full_like(x2, np.nan)), label="FourCastNet", color=colors["fourcastnet"])
    ax.plot(x2, plotted_means.get("tigge", np.full_like(x2, np.nan)), label="HRES", color=colors["HRES"], linewidth=3, linestyle="--")
    ax.plot(x2, plotted_means.get("panguweather", np.full_like(x2, np.nan)), label="PanguWeather", color=colors["panguweather"])
    ax.plot(x2, plotted_means.get("fourcastnetv2", np.full_like(x2, np.nan)), label="FourCastNetv2", color=colors["fourcastnetv2"])
    ax.plot(x2, plotted_means.get("graphcast37", np.full_like(x2, np.nan)), label="GraphCast", color=colors["graphcast37"])
    ax.plot(x2, plotted_means.get("aurora", np.full_like(x2, np.nan)), label="Aurora", color=colors["aurora"])
    
    # Plot standard error with fill_between
    for model_key in models_to_plot:
        # Check if means and sems exist for the model_key (they should due to pre-initialization)
        if model_key in plotted_means and model_key in plotted_sems:
             ax.fill_between(x2, plotted_means[model_key] - plotted_sems[model_key], 
                            plotted_means[model_key] + plotted_sems[model_key], 
                            color=colors.get(model_key, '#808080'), alpha=0.2) # Use .get for color too

    # Set titles and labels
    if var == "TMQ":
        title_str = "Integrated Water Vapor"
        ax.set_ylabel('RMSE of IWV (kg/m²)')
    elif var == "TMQ_bias":
        title_str = "Integrated Water Vapor Bias"
        ax.set_ylabel('Bias of IWV (kg/m²)')
    elif var == "U850": # Updated from WIND850
        title_str = "850hPa U-Wind Component"
        ax.set_ylabel('RMSE of 850hPa U-Wind (m/s)')
    elif var == "V850": # New variable
        title_str = "850hPa V-Wind Component"
        ax.set_ylabel('RMSE of 850hPa V-Wind (m/s)')
    elif var == "WIND850": # New variable
        title_str = "850hPa Wind Magnitude"
        ax.set_ylabel('RMSE of 850hPa Wind (m/s)')
    elif var == "PSL":
        title_str = "Sea Level Pressure"
        ax.set_ylabel('RMSE of SLP (hPa)') # Data is in Pa, label is hPa
    else: # Default case for any other variable
        title_str = f"RMSE for {var}"
        ax.set_ylabel('RMSE') # Generic ylabel
    
    ax.set_title(title_str)
    
    # Set x-axis properties
    ax.set_xticks(np.arange(0, 10.1, 1))  # 0 to 10 days
    if row == 1:  # Bottom panels
        ax.set_xlabel('Lead Time (Days)')
    else:  # Top panels
        ax.set_xticklabels([])
    
    # Add legend only to first panel
    if i == 0:
        ax.legend()

    ax.grid(True, linestyle='--', alpha=0.6) # Add light dashed grid lines

    # Special y-tick handling for PSL, applied after all plotting on `ax` is done for this iteration
    if var == "PSL":
        # It's often better to let matplotlib auto-scale first.
        # Forcing a draw might be intensive in a loop if not necessary.
        # This will apply to the current auto-generated ticks.
        current_yticks = ax.get_yticks()
        ax.set_yticklabels([int(y/100) for y in current_yticks])

fig.suptitle("RMSE on U.S. West Coast vs Lead Time", y=0.97, x=0.51, fontsize=20, fontweight='bold') # Updated title
plt.tight_layout()
if save: plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()
# %%
