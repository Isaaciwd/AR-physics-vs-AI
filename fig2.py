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
save_path = "/glade/work/idavis/AR_CR_project/paper_figs/fig_2.pdf"

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


# ###################################
# Plotting Latitude Landfall Error FOR PAPER
# ###################################
# Font sizes
font_multiplier = 1.3
TITLE_SIZE = 20 * font_multiplier
LABEL_SIZE = 18 * font_multiplier
TICK_SIZE = 18 * font_multiplier

# List of models and configuration
model_list = ["tigge", "graphcast37", "panguweather", "fourcastnet", "fourcastnetv2", "aurora_ft"]
# data_dir = "/glade/work/idavis/AR_CR_project/rmse_data/"
data_dir = "./data/fig_2/"

# Define timesteps and create labels (accounting for 6-hour intervals)
timesteps = [17, 29, 41]
window = 12 # window applied on earlier side of timesteps
timestep_labels = [f'Day {((t-1) * 6) / 24:.1f}' for t in timesteps]
time_window_labels = [f'Days {((t-1-window) * 6) / 24:.1f} - {((t-1) * 6) / 24:.1f}' for t in timesteps]


model_names_capitalized = {
    'graphcast37': 'GraphCast',
    'panguweather': 'PanguWeather',
    'tigge': 'HRES',
    'fourcastnet': 'FourCastNet',
    'fourcastnetv2': 'FourCastNetV2',
    'aurora_ft': 'Aurora'
}

# Initialize data dictionary
data = {t: [] for t in timesteps}

# Load data for each model
for model in model_list:
    filename = os.path.join(data_dir, f"{model}_lat_landfall_error_degrees.pkl")
    # os.system(f"cp {filename} /glade/work/idavis/AR_CR_project/minimally_reproducable_figs/data/fig_2/{model}_lat_landfall_error_degrees.pkl")

    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            all_lle = pickle.load(f)
            for t in timesteps:
                if t <= len(all_lle):
                    errors = all_lle[t-window:t]
                    errors = np.hstack(errors) if isinstance(errors, list) else errors
                    data[t].append(errors)
                else:
                    data[t].append([])
    else:
        print(f"File not found for model: {model}")
        for t in timesteps:
            data[t].append([])


# Keep existing model configuration and data loading code...

# Calculate subplot layout
n_plots = len(timesteps)
n_cols = min(3, n_plots)
n_rows = (n_plots + n_cols - 1) // n_cols
# Create subplot grid with larger figure size
fig, axes = plt.subplots(n_rows, n_cols, figsize=(9*n_cols, 9*n_rows), sharey=True)
axes = np.array(axes).flatten()

# Hide empty subplots
for idx in range(n_plots, len(axes)):
    axes[idx].set_visible(False)

# Create box plots
for idx, t in enumerate(timesteps):
    ax = axes[idx]
    
    # Add zero reference line
    ax.axhline(y=0, color='gray', linestyle='-', alpha=1)
    
    # Create box plot
    positions = np.arange(len(model_list)) + 1
    bp = ax.boxplot(data[t], positions=positions, 
                   patch_artist=True,  # Fill boxes with color
                   medianprops=dict(color="black", linewidth=1.5),
                   flierprops=dict(marker='o', markerfacecolor='gray', 
                                 markersize=4, alpha=1),
                   showfliers=False,
                   widths=0.7)
    
    # Color boxes
    for i, box in enumerate(bp['boxes']):
        box.set_facecolor(colors[model_list[i]])
        box.set_alpha(1)
    
    # Set title and labels
    ax.set_title(f'Latitude Landfall Error {time_window_labels[idx]}', fontsize=TITLE_SIZE)
    if idx % n_cols == 0:
        ax.set_ylabel('Latitude Error (degrees)', fontsize=LABEL_SIZE)
    
    # Only show x-labels for bottom row
    is_bottom_row = idx >= n_plots - n_cols
    if is_bottom_row:
        ax.set_xticks(positions)
        ax.set_xticklabels([model_names_capitalized[model] for model in model_list], 
                          rotation=30, 
                          fontsize=TICK_SIZE)
    else:
        ax.set_xticklabels([])
        ax.set_xticks([])
    
    # Increase tick label size for y-axis
    ax.tick_params(axis='y', labelsize=TICK_SIZE)
    ax.grid(True, linestyle='--', alpha=0.6) # Add light dashed grid lines


plt.suptitle("USWC Meridional Landfall Error at Various Lead Times", y=0.985,fontsize=TITLE_SIZE+3, fontweight='bold')

plt.tight_layout()
if save:
    plt.savefig(save_path, dpi=300, bbox_inches='tight')

plt.show()
#%%
