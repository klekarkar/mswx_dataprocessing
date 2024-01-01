
"""
### Function to extract MSWX/MSWEP climate data as timeseries

Created by: Katoria Lekarkar 05/11/2023
Licence: CC BY

"""
#import libraries
import os
import xarray as xr
import matplotlib.pyplot as plt
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
    src_path=src_path

    #list all files in parent folder
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
            var_data=xr.open_dataset(os.path.join(src_path,file), engine='netcdf4')
            
            #clip file to reduce size for computation
            subset_data=var_data.sel(lon=slice(min_lon,max_lon), lat=slice(max_lat,min_lat)) 
            lat=subset_data.variables['lat'][:]
            lon=subset_data.variables['lon'][:]
            
            #squared difference of lat and lon
            sq_diff_lat=(lat-stat_lat)**2
            sq_diff_lon=(lon-stat_lon)**2

            #locate the index nearest point (minimum value) of station from the data file
            min_indexlat=np.argmin(sq_diff_lat.data)
            min_indexlon=np.argmin(sq_diff_lon.data)
        
            #accessing the data
            var_climate_data=subset_data.variables[glo_var] #access the climate variable from the file using the variable name
            date_range=pd.to_datetime(subset_data.time) #access time from the file

            for time_index in np.arange(0, len(date_range)):
                row_label = date_range[time_index]
                col_label = glo_var

                # Update the cell in the DataFrame with the value of the variable
                station_timeseries.loc[row_label, col_label] = var_climate_data[time_index, min_indexlat, min_indexlon]
                station_timeseries.index.name='date'
            
        #save to data dir with station name and variable        
        station_timeseries.to_csv(os.path.join(src_path,station+'_mswx'+'_'+glo_var+'.csv')) 

        print('Recorded data for', station)

if __name__ == "__main__":
    print('Extracting data...')

        
