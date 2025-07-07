#%%
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from datetime import datetime, timedelta
import os
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
import matplotlib.colorbar as mcolorbar
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import holoviews as hv
import matplotlib as mpl
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# dates of interest at 4 day lead time
# 20231125_00, 20231210_00, 20231215_00, 20231215_00, 20231215_00, 20231215_00, 20231215_00

# Parameters
save = False
save_path = "/glade/work/idavis/AR_CR_project/paper_figs/fig4_models.pdf"
darkmode = False
diff = True # Set to True for difference plots with ERA5, False for absolute values
valid_time = "20240315_00"  # format: YYYYMMDD_HH
lead_times = [7]  # days before valid time
extent = [-180, -109.99, 15, 60.01]
model_list = [ "graphcast37","tigge", "aurora_ft", "fourcastnet", "fourcastnetv2", "panguweather"]
plot_quiver_key = 1
plot_x_labels = True
plot_y_labels = True
plot_colorbar = 1
plot_ar_outline = 1
print(valid_time)
font_multiplier = 2.15
plt.rcParams['font.size'] = 17 * font_multiplier
plt.rcParams['axes.labelsize'] = 17 * font_multiplier
plt.rcParams['axes.titlesize'] = 15 * font_multiplier
plt.rcParams['xtick.labelsize'] = 15 * font_multiplier
plt.rcParams['ytick.labelsize'] = 15 * font_multiplier
plt.rcParams['legend.fontsize'] = 17 * font_multiplier
plt.rcParams['figure.titlesize'] = 15 * font_multiplier

if darkmode:
    # Custom colormap using the extracted RGB values
    normalized_colors = np.array([
        [0.49803922, 0.24705882, 0.64705882],
        [0.38823529, 0.05098039, 0.48627451],
        [0.60392157, 0.03529412, 0.32156863],
        [0.81176471, 0.03529412, 0.16078431],
        [0.98823529, 0.05490196, 0.10588235],
        [0.98823529, 0.23137255, 0.11372549],
        [0.99215686, 0.44313725, 0.13333333],
        [0.99215686, 0.65098039, 0.16078431],
        [0.99607843, 0.76470588, 0.18039216],
        [0.99607843, 0.87843137, 0.2       ],
        [1.        , 0.99215686, 0.21960784],

        [0.1, 0.1, 1      ],

        [0.70196078, 0.90196078, 0.18039216],
        [0.39607843, 0.80784314, 0.14901961],
        [0.12156863, 0.71372549, 0.12941176],
        [0.12156863, 0.78431373, 0.34117647],
        [0.14509804, 0.88235294, 0.63529412],
        [0.16862745, 0.97647059, 0.9254902 ],
        [0.12941176, 0.77254902, 0.99215686],
        [0.07843137, 0.45882353, 0.98431373],
        [0.04313725, 0.18039216, 0.98431373],
        [0.02745098, 0.10588235, 0.78823529],
        [1.        , 1.        , 1.        ]
    ])

    # flip the colormap to match the data
    normalized_colors = normalized_colors[::-1]

    # Add an alpha channel to the RGB values
    rgba_colors = np.concatenate([normalized_colors, np.ones((normalized_colors.shape[0], 1))], axis=1)

    # Set the alpha value of the color you want to make transparent
    # In this example, we're making the first color fully transparent
    rgba_colors[0, 3] = 0

    # Create the colormap with the RGBA values
    custom_cmap = mcolors.ListedColormap(rgba_colors)

    plt.style.use('dark_background')

else: custom_cmap = plt.cm.get_cmap('coolwarm')
# Custom colormap if needed (ensure it's defined or adjust as necessary)
# Assuming custom_cmap is defined earlier in your code
# If not, you can define it here or replace 'cmap = custom_cmap' with a standard colormap

# Create subplot grid for 2 rows (one per lead time)
# mpl.rcParams['figure.dpi'] = 40
n_cols = 2
n_rows = 3
# fig, axes = plt.subplots(n_rows, n_cols, figsize=(11 * n_cols, 7 * n_rows), 
#                         subplot_kw={'projection': ccrs.PlateCarree()})

# fig.subplots_adjust(left=0.1,  wspace=1.5)  # Make room for lead time labels
fig = plt.figure(figsize=(11 * n_cols, 7 * n_rows))
gs = mpl.gridspec.GridSpec(n_rows, n_cols, figure=fig, wspace= 0)  # Increase wspace to add more horizontal space

axes = []
for row in range(n_rows):
    for col in range(n_cols):
        ax = fig.add_subplot(gs[row, col], projection=ccrs.PlateCarree())
        axes.append(ax)
idx = -1
# Main plotting loop
for lead_idx, lead_time in enumerate(lead_times):
    # Calculate initialization date
    valid_dt = datetime.strptime(valid_time, "%Y%m%d_%H")
    init_dt = valid_dt - timedelta(days=lead_time)
    init_date = init_dt.strftime("%Y%m%d")
    
    # Calculate time step based on lead time
    time_step = lead_time * 4  # Assuming 6-hourly data (4 timesteps per day)
    
    for model_idx, model in enumerate(model_list):
        idx+=1
        ax = axes[idx]
        # Load data from the combined file
        ds_combined = xr.open_dataset(f"./data/fig_4/{model}_combined.nc")

        # Extract variables for plotting
        U850 = ds_combined['U850'].values
        V850 = ds_combined['V850'].values
        PSL = ds_combined['PSL'].values
        TMQ = ds_combined['TMQ'].values
        ar_mask_model = ds_combined['ar_mask'].values
        lons = ds_combined['lon'].values
        lats = ds_combined['lat'].values

        # Plotting
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        xlocs_lines = np.arange(-180, -110, 5)
        ylocs_lines = np.arange(10, 70, 5)

        # Define locations for labels
        xlocs_labels = np.array([-175,-155,-135,-115])
        ylocs_labels = np.arange(20, 70, 10)

        TMQ = np.where(TMQ > 60, 60, TMQ)
        if diff:
            if model == "ERA5":
                levels = np.arange(18, 64, 2)
                cmap = custom_cmap
            else:
                def create_bkr_cmap(n_colors=256, center_transparent=True):
                    # Create blue to black to red color gradient
                    blues = np.array([(0, 0, i/128, 1) for i in range(128)])
                    reds = np.array([(i/128, 0, 0, 1) for i in range(128)])
                    
                    # Combine with black in center
                    colors = np.vstack((blues[::-1], reds))
                    
                    # Add transparency to center if requested
                    if center_transparent:
                        center_idx = len(colors) // 2
                        width = 10  # Width of transparent region
                        colors[center_idx-width:center_idx+width, 3] = 0
                    
                    return mcolors.ListedColormap(colors)

                # Create discrete levels
                levels = np.arange(-25, 26, 2)
                if darkmode: cmap = create_bkr_cmap()
                else: cmap = custom_cmap
                # Create BoundaryNorm for discrete colors
                norm = mcolors.BoundaryNorm(levels, cmap.N)
                
                # Update contourf with norm parameter
                cf_tmq = ax.contourf(lons, lats, TMQ, 
                                    levels=levels, 
                                    cmap=cmap, 
                                    norm=norm,
                                    transform=ccrs.PlateCarree())

        else:
            levels = np.arange(18, 64, 2)
            cmap = custom_cmap  # Ensure custom_cmap is defined

            cf_tmq = ax.contourf(lons, lats, TMQ, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())

        # # # # AR mask outline

        if plot_ar_outline:
            ar_contour = ax.contour(lons, lats, ar_mask_model, levels=[0.5], colors='k', linewidths=3., linestyles="--", transform=ccrs.PlateCarree())
            ar_outline_proxy = Line2D([0], [0], color='k', linewidth=3., linestyle="--", label='AR Outline')
            if idx == 0: ax.legend(handles=[ar_outline_proxy], loc='lower right', bbox_to_anchor=(1, 0), prop={'size': 20}, frameon=True)

        # Sea level pressure contours - set color based on darkmode
        contour_color = "gray" if darkmode else "dimgray"  # Gray in dark mode, dark gray in light mode
        
        if diff and model != "ERA5":
            cf_psl = ax.contour(lons, lats, PSL, levels=np.arange(-30, 34, 4), colors=contour_color, linewidths=1, transform=ccrs.PlateCarree())
            cf_psl_2 = ax.contour(lons, lats, PSL, levels=np.arange(-28, 30, 4), colors=contour_color, linewidths=1, transform=ccrs.PlateCarree())
        else:
            cf_psl = ax.contour(lons, lats, PSL, levels=np.arange(952, 1048, 4), colors=contour_color, linewidths=1, transform=ccrs.PlateCarree())
            cf_psl_2 = ax.contour(lons, lats, PSL, levels=np.arange(954, 1046, 4), colors=contour_color, linewidths=1, transform=ccrs.PlateCarree())
        
        # Set contour label colors and background to maintain readability
        label_color = "black" if not darkmode else "white"
        labels = ax.clabel(cf_psl, inline=True, fontsize=20, fmt='%d', colors=label_color)
        for label in labels:
            label.set_bbox(dict(facecolor='white' if not darkmode else 'black', edgecolor='none', pad=2, alpha=0.8))

        # Wind barbs - set color based on darkmode
        barb_slice = slice(None, None, 10)
        quiver_color = "w" if darkmode else "k"  # White in dark mode, black in light mode
        Q = ax.quiver(lons[barb_slice], lats[barb_slice], U850[barb_slice, barb_slice], V850[barb_slice, barb_slice], 
                     pivot='middle', transform=ccrs.PlateCarree(), scale=450, color=quiver_color)

        # Set coastline color based on darkmode
        coastline_color = "w" if darkmode else "k"  # White in dark mode, black in light mode
        ax.add_feature(cfeature.COASTLINE.with_scale('110m'), edgecolor=coastline_color, linewidth=3)

        # Gridlines
        # Determine if this plot is in the leftmost column or bottom row
        is_leftmost = (idx % n_cols == 0)
        is_bottom_row = (idx // n_cols == n_rows - 1)

        # Draw gridlines with labels based on position
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=True,
            linewidth=1,
            color='black',
            alpha=0,
            linestyle='--',
            xlocs=xlocs_labels, # Use the defined label locations
            ylocs=ylocs_labels
        )
        gl.top_labels = False
        gl.right_labels = False
        # Only show left labels if it's the leftmost plot and plot_y_labels is True
        gl.left_labels = is_leftmost and plot_y_labels
        # Only show bottom labels if it's the bottom row plot and plot_x_labels is True
        gl.bottom_labels = is_bottom_row and plot_x_labels

        # Format labels (optional, but good practice)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 15 * font_multiplier, 'color': 'black'}
        gl.ylabel_style = {'size': 15 * font_multiplier, 'color': 'black'}


        if plot_quiver_key and idx == 0:
            # Set quiver key box colors based on darkmode
            rect_facecolor = 'k' if darkmode else 'white'
            rect_edgecolor = 'w' if darkmode else 'k'
            white_rect = Rectangle((0.792, 0.9), 0.2, 0.09, facecolor=rect_facecolor, edgecolor=rect_edgecolor, transform=ax.transAxes, zorder=7, alpha=0.8)
            ax.add_patch(white_rect)
            
            # Set quiver key text color based on darkmode
            label_color = "white" if darkmode else "black"
            key = ax.quiverkey(Q, X=0.845, Y=0.94, U=20, label='20 m/s', labelpos='E', 
                              labelcolor=label_color, color=quiver_color, 
                              coordinates='axes', fontproperties={'size': 23})
            # white_rect = Rectangle((0.83, 0.895), 0.17, 0.09, facecolor=rect_facecolor, edgecolor=rect_edgecolor, transform=ax.transAxes, zorder=7, alpha=0.8)
            # ax.add_patch(white_rect)
            
            # # Set quiver key text color based on darkmode
            # label_color = "white" if darkmode else "black"
            # key = ax.quiverkey(Q, X=0.845, Y=0.933, U=10, label='10 m/s', labelpos='E', 
            #                   labelcolor=label_color, color=quiver_color, 
            #                   coordinates='axes', fontproperties={'size': 17})
            key.set_zorder(8)

        # Title
        model_name_map = {
            "graphcast37": "GraphCast",
            "tigge": "HRES",
            "fourcastnet": "FourCastNet",
            "fourcastnetv2": "FourCastNetV2",
            "panguweather": "PanguWeather",
            "aurora_ft": "Aurora"
        }
        display_model_name = model_name_map.get(model, model.capitalize()) # Use mapped name or capitalize original

        # valid_time_str = ds.time[time_step].values
        # init_time_str = ds.time[0].values

        # Set title for all plots
        ax.set_title(display_model_name, pad=5, fontsize=18*font_multiplier) # Increased pad slightly

# Hide any unused subplots (if n_rows*n_cols > len(model_list)*len(lead_times))
# for ax_to_hide in axes[len(model_list) * len(lead_times):]:
#     ax_to_hide.set_visible(False)


plt.suptitle(f'7-Day Lead Time Forecasts Minus ERA5',x=0.5, y=0.96, fontsize=20*font_multiplier)

# Adjust layout - might need tweaking depending on final figure size and labels
fig.subplots_adjust(left=0.05, right=0.88, bottom=0.05, top=0.9, wspace=0.6, hspace=0.12) # Adjusted spacing

if plot_colorbar:
    # Position colorbar relative to the figure
    cax = fig.add_axes([0.893, 0.108, 0.025, 0.772]) # Adjust position/size as needed
    
    if diff:
        norm = mcolors.BoundaryNorm(levels, cmap.N) # Use the norm created earlier
        cbar = fig.colorbar(cf_tmq, 
                        cax=cax, 
                        norm=norm,
                        boundaries=levels,
                        ticks=levels[::2]) # Use levels for boundaries and ticks
        cbar.set_label('IWV Difference (mm)', labelpad=0)
        cbar.set_ticks(np.arange(levels[0], levels[-1]+1, 5)) # Adjust tick frequency if needed
    else:
        norm = plt.Normalize(levels[0], levels[-1])
        cbar = fig.colorbar(cf_tmq, cax=cax, norm=norm)
        cbar.set_label('Integrated Water Vapor (mm)')
        cbar.set_ticks(np.arange(levels[0], levels[-1]+1, 6)) # Adjust tick frequency if needed


if save:
    # plt.savefig(f"/glade/work/idavis/AR_CR_project/final_plots/{valid_time}_case_study_4d_pretty.png", dpi=300, bbox_inches='tight')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()

# %%
