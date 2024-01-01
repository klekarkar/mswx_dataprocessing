
"""
### Function to extract MSWX/MSWEP climate data as timeseries

Created by: Katoria Lekarkar 05/11/2023
Licence: CC BY

"""
#import libraries
import os
import xarray as xr
import numpy as np
import pandas as pd


"""
These are the variables names to parse for each gloh20 climate variable:  

precipitation: 'precipitation' [mm/day]  
relative humidity: 'relative_humidity' [%]  
wind: 'wind_speed' [m/s]  
Tmax: 'air_temperature' [degree_celcius]  
Tmin: 'air_temperature' [degree_celcius]
short-wave solar radiation: 'downward_shortwave_radiation'
"""

def get_gloh2o_timeseries(src_path, var_stations_file,glo_var,min_lon,max_lon,max_lat,min_lat):   #bounding_box top left to bottom right
    #stations
    var_stations=pd.read_csv(var_stations_file) #stations

    #use list comprehension to list all nc files in source folder
    files=[file for file in os.listdir(src_path) if file.endswith('.nc')]

    #get the start year and day of the first file
    start_year=files[0][0:4]
    start_day=files[0][5:7]

    #create zeros df and the weather variable to extract and generate daterange equal to len of all files on daily basis
    date_range=pd.date_range(start=str(start_year)+'-01-'+str(start_day), periods=len(files), freq='D') 
    station_timeseries=pd.DataFrame(0.0,columns=[glo_var], index=date_range) 

    #define bounding box to extract subset of global data to fasten computation
    # min_lat=-10
    # max_lat=10
    # min_lon=32
    # max_lon=40

    for index, row in var_stations.iterrows():
        station=row['station_name']
        stat_lat=row['lat']
        stat_lon=row['lon']
        
        for file in files:   
            file_path = os.path.join(src_path, file)   
            with xr.open_dataset(file_path, engine='netcdf4') as var_data:       
                           
                    #clip file to reduce size for computation
                    subset_data=var_data.sel(lon=slice(min_lon,max_lon), lat=slice(max_lat,min_lat)) 
                    # Select the nearest data point for the station
                    nearest_data = subset_data.sel(lon=stat_lon, lat=stat_lat, method='nearest')

                    # Accessing the data
                    var_climate_data = nearest_data[glo_var]  # Access the climate variable
                    date_range = pd.to_datetime(nearest_data.time)  # Access time from the file

                    for time_index in np.arange(0, len(date_range)):
                        row_label = date_range[time_index]
                        col_label = glo_var

                        # Update the DataFrame with the value of the variable
                        station_timeseries.loc[row_label, col_label] = var_climate_data[time_index]
                        station_timeseries.index.name = 'date'
                        print(f'extracted data for {var_data}')

        #save to data dir with station name and variable        
        station_timeseries.to_csv(os.path.join(src_path,station+'_mswx'+'__'+glo_var+'.csv')) 

        print('Recorded data for', station)

if __name__ == "__main__":
    src_path = 'path/to/data'
    var_stations_file = 'path/to/stations.csv'
    glo_var = 'precipitation'  # Example variable
    min_lon, max_lon, max_lat, min_lat = -10, 40, 10, -10  # Bounding box coordinates

    get_gloh2o_timeseries(src_path, var_stations_file, glo_var, min_lon, max_lon, max_lat, min_lat)
