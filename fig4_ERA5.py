#%%
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import matplotlib.colors as mcolors
import matplotlib.colorbar as mcolorbar
from datetime import datetime
import os
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
#%%
# Add darkmode parameter
darkmode = False  # Set to False for light mode
save = False
save_path = "/glade/work/idavis/AR_CR_project/paper_figs/fig_4.pdf"


# DO NOT CHANGE THESE PARAMETERS
diff = False
date = "20240315"
model = "ERA5"
n_days = 0   # number of days/ hours out from initialization to show on the plot
n_hours = 0
extent =[-180, -109.99, 15, 60.01]
plot_quiver_key = 1
plot_x_labels = True
plot_y_labels = True
plot_colorbar = 1
plot_ar_outline = True
plot_lat_lon_ticks = True  # New parameter to control latitude/longitude tick display

if n_hours%6 != 0:
    raise ValueError('n_hours must be a multiple of 6')
if darkmode:
    plt.style.use('dark_background')
else:
    plt.style.use('default')

font_multiplier = 2.9
# Set the default text sizes
plt.rcParams['font.size'] = 17 * font_multiplier # Adjust to make text larger or smaller
plt.rcParams['axes.labelsize'] = 17 * font_multiplier
plt.rcParams['axes.titlesize'] = 15 * font_multiplier
plt.rcParams['xtick.labelsize'] = 13 * font_multiplier
plt.rcParams['ytick.labelsize'] = 13 * font_multiplier
plt.rcParams['legend.fontsize'] = 17 * font_multiplier
plt.rcParams['figure.titlesize'] = 15 * font_multiplier
diff_str = ""

time_step = n_days * 4 + n_hours

ds = xr.open_dataset(f"/glade/campaign/univ/ucub0156/runs/processed/{date}/{model}/{model}.nc")
if model == "fourcastnet":
    ds = ds.isel(lat=slice(0,-1))
ar_mask = xr.open_dataset(f"/glade/campaign/univ/ucub0156/runs/masked/{date}/{model}_processed.nc")["class_masks"]

if model == "fourcastnet":
    ds = ds.isel(lat=slice(0,-1))


# Get the Unix timestamp from the dataset
timestamp = ds['time'][time_step].values.astype(int)

# Convert the Unix timestamp from nanoseconds to seconds
timestamp_in_seconds = timestamp / 1e9

# Convert the Unix timestamp to a datetime object in UTC
dt = datetime.utcfromtimestamp(timestamp_in_seconds)

hour = dt.hour
day = dt.date()

if hour != 0:
    time_step = time_step - 1

    # Get the Unix timestamp from the dataset
    timestamp = ds['time'][time_step].values.astype(int)

    # Convert the Unix timestamp from nanoseconds to seconds
    timestamp_in_seconds = timestamp / 1e9

    # Convert the Unix timestamp to a datetime object in UTC
    dt = datetime.utcfromtimestamp(timestamp_in_seconds)

    hour = dt.hour
    day = dt.date()


print(f"Initialized {date} 0000 UTC, Valid: {dt} UTC, {model}")
print(f"ds: Valid {ds.time[time_step].values} UTC")

# Load data from the combined file
ds_combined = xr.open_dataset(f"./data/fig_4/{model}_combined.nc")

# Extract variables for plotting
U850 = ds_combined['U850'].values
V850 = ds_combined['V850'].values
PSL = ds_combined['PSL'].values
TMQ = ds_combined['TMQ'].values
ar_mask = ds_combined['ar_mask'].values
lons = ds_combined['lon'].values
lats = ds_combined['lat'].values

if diff:
    # This block might need adjustment depending on what `diff` is supposed to do with combined files.
    # For now, assuming `diff` is false for the ERA5 base plot.
    pass

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

if plot_colorbar: fig = plt.figure(figsize=(16.8, 10.8))
else: fig = plt.figure(figsize=(11.5111, 7.4))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent, crs=ccrs.PlateCarree())  # Set the map extent
# Define the intervals for the gridlines
xlocs_lines = np.arange(-180, -110, 5)
ylocs_lines = np.arange(10, 70, 5)

if plot_x_labels and not plot_lat_lon_ticks: 
    xlocs_labels = np.arange(-180, -110, 10)
else: 
    xlocs_labels = np.arange(0)
if plot_y_labels and not plot_lat_lon_ticks: 
    ylocs_labels = np.arange(20, 70, 10)
else: 
    ylocs_labels = np.arange(0)

# Set ticks and labels based on plot_lat_lon_ticks flag
if plot_lat_lon_ticks:
    # Turn off all tick labels first
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Define coordinates for ticks
    xlocs_labels = np.array([-175, -155, -135, -115])
    ylocs_labels = np.arange(20, 70, 10)
    
    # For a single plot, we'd typically want both longitude and latitude ticks
    ax.set_xticks(xlocs_labels)
    ax.set_xticklabels([f"{abs(x)}°W" for x in xlocs_labels])
    ax.set_yticks(ylocs_labels)
    ax.set_yticklabels([f"{y}°N" for y in ylocs_labels])

# Plot the integrated water vapor (TMQ) as a filled contour
TMQ = np.where(TMQ > 60, 60, TMQ) # set values greater than 60 to 60, to simulate an open upper interval
if diff: 
    levels = np.arange(-25, 26, 2)
    cmap = "coolwarm"
else: 
    levels = np.arange(18, 64, 2)
    cmap = custom_cmap
cf_tmq = ax.contourf(lons, lats, TMQ, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
if plot_colorbar:
    cbar_tmq = plt.colorbar(cf_tmq, ax=ax, pad=0.03, shrink=0.8, aspect=8)
    cbar_tmq.set_label('Integrated Water Vapor\n(mm)', fontsize=36, labelpad=15)
    cbar_tmq.set_ticks(np.arange(levels[0], levels[-1]+1, 10))
    cbar_tmq.ax.tick_params(labelsize=32) 

# shade in the AR mask orange
# Draw a line around the edge of the AR mask

if plot_ar_outline:
    if darkmode: outline_color = 'red'
    else: outline_color = 'k'
    ar_contour = ax.contour(lons, lats, ar_mask, levels=[0.5], colors=outline_color, linewidths=3, linestyles="--",transform=ccrs.PlateCarree(), label = "AR Outline")
    # ar_shading = ax.contourf(lons, lats, ar_mask, levels=[0.5, 1.5], colors='yellowgreen', alpha=0.2, transform=ccrs.PlateCarree(), zorder=10)
    print(outline_color)
    # Step 1: Create a proxy artist for the contour line
    ar_outline_proxy = Line2D([0], [0], color=outline_color, linewidth=3, linestyle="--", label='AR Outline')

    # Step 2: Create the legend with the proxy artist, move it, and make it smaller
    ax.legend(handles=[ar_outline_proxy], loc='lower right', bbox_to_anchor=(1, 0), prop={'size': 25}, frameon=True)


# Plot the sea level pressure contours
if diff:
    cf_psl = ax.contour(lons, lats, PSL, levels=np.arange(-30, 34, 4), colors='gray', linewidths=1, transform=ccrs.PlateCarree())
    cf_psl_2 = ax.contour(lons, lats, PSL, levels=np.arange(-28, 30, 4), colors='gray', linewidths=1, transform=ccrs.PlateCarree())
    labels = ax.clabel(cf_psl, inline=True, fontsize=14, fmt='%d',  colors='black' if not darkmode else 'white')

else:
    cf_psl = ax.contour(lons, lats, PSL, levels=np.arange(952, 1048, 4), colors='gray', linewidths=1, transform=ccrs.PlateCarree())
    cf_psl_2 = ax.contour(lons, lats, PSL, levels=np.arange(954, 1048, 4), colors='gray', linewidths=1, transform=ccrs.PlateCarree())
    labels = ax.clabel(cf_psl, inline=True, fontsize=20, fmt='%d',  colors='black' if not darkmode else 'white')
    # Add a white box around the contour labels
for label in labels:
    label.set_bbox(dict(facecolor='white' if not darkmode else 'black', edgecolor='none', pad=2, alpha=0.8))

# Plot the wind barbs for every 20th value
barb_slice = slice(None, None, 10)
Q = ax.quiver(lons[barb_slice], lats[barb_slice], U850[barb_slice, barb_slice], V850[barb_slice, barb_slice], pivot='middle', transform=ccrs.PlateCarree(), scale=450, color="white" if darkmode else "black")

# Set coastline color based on darkmode
coastline_color = 'w' if darkmode else 'k'
ax.add_feature(cfeature.COASTLINE.with_scale('110m'), edgecolor=coastline_color, linewidth=3)
# ax.add_feature(cfeature.LAND, facecolor='lightgray')


# # Add gridlines at the specified intervals
# gridlines_lines = ax.gridlines(draw_labels=False, xlocs=xlocs_lines, ylocs=ylocs_lines, linestyle=(0, (15, 5)))
# gridlines_labels = ax.gridlines(draw_labels=True, xlocs=xlocs_labels, ylocs=ylocs_labels, linestyle=(0, (15, 5)))

# # Disable labels where gridlines are drawn
# gridlines_labels.top_labels = False
# gridlines_labels.right_labels = False

if plot_quiver_key:
    # Add a quiver key (scale)
    # Parameters: (x, y) in axis-relative coordinates, width, height in axis-relative coordinates
    # Position the rectangle in the top-right corner with a small margin
    rect_color = 'k' if darkmode else 'w'
    text_color = 'w' if darkmode else 'k'
    white_rect = Rectangle((0.792, 0.9), 0.2, 0.09, facecolor=rect_color, edgecolor=coastline_color, transform=ax.transAxes, zorder=7, alpha=0.8)
    # Add the rectangle to the plot
    ax.add_patch(white_rect)
    key = ax.quiverkey(Q, X=0.85, Y=0.94, U=20, label='20 m/s', labelpos='E', color=text_color,fontproperties={'size': 25})
    # key.vector.set_facecolor('w')
    # key.text.set_backgroundcolor('w')
    key.set_zorder(8)

    # white_rect = Rectangle((0.82, 0.895), 0.17, 0.09, facecolor='k', edgecolor='none', transform=ax.transAxes, zorder=7, alpha = 0.8)
    # ax.add_patch(white_rect)
    # key = ax.quiverkey(Q, X=0.865, Y=0.935, U=10, label='10 m/s', labelpos='E', labelcolor = "white", color = "white", coordinates='axes', fontproperties={'size': 15})
    # key.set_zorder(8)

# capitalize the first lwtter of model
model = model.capitalize()
if model == 'Tigge':
    model = 'HRES'


# plt.title(f"ERA5:  Valid {dt} UTC\n IWV$_{{(mm;\\ shaded)}}$, 850-hPa Wind$_{{(m/s;\\ vectors)}}$, SLP$_{{(hPa;\\ contours)}}$", x=0.5, y=1.08)
plt.title(f"ERA5: Valid 2024-03-15 00 UTC", y=1.03)


if save:
    # # check if file already exists
    # darkmode_str = "_dark" if darkmode else "_light"
    # if os.path.exists(f"/glade/work/idavis/AR_CR_project/figures/plot_like_cw3e/{model}_{date}_valid_{day}_{hour}{darkmode_str}{diff_str}.png"):
    #     # prompt user if they would like to save th figure
    #     # save = input("Would you like to overwrite the figure? (y/n): ")
    #     save = "y"
    #     if save == 'y':
    #         plt.savefig(f"/glade/work/idavis/AR_CR_project/figures/plot_like_cw3e/{model}_{date}_valid_{day}_{hour}{darkmode_str}{diff_str}.png", dpi=300, bbox_inches='tight')
    # else:
    #     plt.savefig(f"/glade/work/idavis/AR_CR_project/figures/plot_like_cw3e/{model}_{date}_valid_{day}_{hour}{darkmode_str}{diff_str}.png", dpi=300, bbox_inches='tight')

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()
# %%
