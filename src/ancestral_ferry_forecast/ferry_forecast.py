import xarray
import numpy
from pyproj import Proj
import matplotlib.pyplot as plot

fp = '20250530T1800Z-B20250530T0700Z-wind_speed_at_10m.nc'

# Open the NetCDF file using xarray
ds = xarray.open_dataset(fp)

# Define the latitude and longitude of the location
latitude = 53.7989  # Example latitude
longitude = -17.555 # Example longitude

# Manually construct the projection parameters
proj_params = {
    'proj': 'laea',
    'lat_0': ds['lambert_azimuthal_equal_area'].attrs['latitude_of_projection_origin'],
    'lon_0': ds['lambert_azimuthal_equal_area'].attrs['longitude_of_projection_origin'],
    'x_0': ds['lambert_azimuthal_equal_area'].attrs['false_easting'],
    'y_0': ds['lambert_azimuthal_equal_area'].attrs['false_northing'],
    'a': ds['lambert_azimuthal_equal_area'].attrs['semi_major_axis'],
    'b': ds['lambert_azimuthal_equal_area'].attrs['semi_minor_axis'],
    'datum': 'WGS84'
}
proj = Proj(proj_params)

# Convert latitude and longitude to projection coordinates
x_proj, y_proj = proj(longitude, latitude)

# Extract the projection coordinates
x_coords = ds['projection_x_coordinate'].values
y_coords = ds['projection_y_coordinate'].values

# Ensure x_coords and y_coords are compatible for plotting
if x_coords.ndim == 1 and y_coords.ndim == 1:
    x_coords, y_coords = numpy.meshgrid(x_coords, y_coords)

# Find the closest indices to the converted coordinates
x_index = numpy.argmin(numpy.abs(x_coords[0] - x_proj))
y_index = numpy.argmin(numpy.abs(y_coords[:, 0] - y_proj))

# Access the wind speed data at the location
wind_speed = ds['wind_speed'][:, y_index, x_index].values

print(f"Wind speed at location (lat: {latitude}, lon: {longitude}):")
print(wind_speed)

# Plot the projection coordinates and mark the location
plot.figure(figsize=(10, 8))
plot.scatter(x_coords, y_coords, s=1, label='Projection Coordinates')
plot.scatter(x_proj, y_proj, color='red', label='Checked Location')
plot.xlabel('Projection X Coordinate')
plot.ylabel('Projection Y Coordinate')
plot.title('Projection Coordinates and Checked Location')
plot.legend()
plot.grid()
plot.show()
 