
"""
Function to extract MSWX/MSWEP (www.gloh20.org) netcdf climate data files as timeseries

Created by: Katoria Lekarkar 05/11/2023
Licence: CC BY
***************************************************************************************************************************************

These are the variables names to pass as arguments for each gloh20 climate variable:  

precipitation: 'precipitation' [mm/day]  
relative humidity: 'relative_humidity' [%]  
wind: 'wind_speed' [m/s]  
Tmax: 'air_temperature' [degree_celcius]  
Tmin: 'air_temperature' [degree_celcius]
short-wave solar radiation: 'downward_shortwave_radiation' [Wm-2]
"""

#import libraries
import os
import xarray as xr
import numpy as np
import pandas as pd

def get_gloh2o_timeseries(src_path, met_stations_file,glo_var,min_lon,max_lon,max_lat,min_lat):

    #************************************************************************************************************************************************
    #src_path: defines the directory where the files are stored
    #glo_var: defines the meteorological variable being extracted e.g. Tmax is 'air_temperature' refer to the doc string above for all variables
    #met_stations_file: the csv file with station names and coordinates in WGSEPSG 4326 (geographical coordinates). the headers are station_name, lat and lon.

    #min_lon,max_lon,max_lat,min_lat: define the bounding box to extract subset of global data to fasten computation. 
    #Construct a grid around your study area and use the coordinates of the corners. the order of coordinates is top left to bottom right
    #e.g. this is for a rectangle around Kenya.
    # min_lat=-10
    # max_lat=10
    # min_lon=32
    # max_lon=40
    #************************************************************************************************************************************************       
    #Read weather stations
    met_stations=pd.read_csv(met_stations_file) #stations
    src_path=src_path

    #list all files in parent folder
    files=[file for file in os.listdir(src_path) if file.endswith('.nc')]

    #get the start year and day of the first file. The files are named with the format 'yyyydoy (year+julian day) e.g 19790101 is 1979001'
    start_year=files[0][0:4]
    start_day=files[0][5:7]

    #create zeros dataframe and the weather variable to extract and generate daterange equal to len of all files on daily basis
    date_range=pd.date_range(start=str(start_year)+'-01-'+str(start_day), periods=len(files), freq='D') 
    station_timeseries=pd.DataFrame(0.0,columns=[glo_var], index=date_range) 

    for index, row in met_stations.iterrows():
        station=row['station_name']
        stat_lat=row['lat']
        stat_lon=row['lon']
        
        for file in files:  
            #open each nc files and close after processing to optimize memory and speed    
            with xr.open_dataset(os.path.join(src_path, file), engine='netcdf4') as var_data:  

                # Clip file to reduce size for computation
                subset_data = var_data.sel(lon=slice(min_lon, max_lon), lat=slice(max_lat, min_lat))

                # Select data from the closest grid to the station.
                #The sel nearest method is fractionally faster than calculating the nearest lat/lon.(shown below)
                nearest_data = subset_data.sel(lon=stat_lon, lat=stat_lat, method='nearest')

                #This method also works but takes longer
                """
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
                """
                # Accessing the data
                var_climate_data = nearest_data[glo_var]  # Access the climate variable
                date_range = pd.to_datetime(nearest_data.time)  # Access time from the file

                for time_index in np.arange(0, len(date_range)):
                    row_label = date_range[time_index]
                    col_label = glo_var

                    # Update the DataFrame with the value of the variable
                    station_timeseries.loc[row_label, col_label] = var_climate_data[time_index]
                station_timeseries.index.name = 'date'
        #save to data dir with station name and variable        
        station_timeseries.to_csv(os.path.join(src_path,station+'_mswx'+'_'+glo_var+'.csv')) 

        print('Recorded data for', station)

if __name__ == "__main__":
    src_path = 'path/to/data'
    met_stations = 'path/to/stations.csv'
    glo_var = 'precipitation'
    min_lon, max_lon, max_lat, min_lat = 'x1', 'x2', 'y2', 'y1'
    get_gloh2o_timeseries(src_path, met_stations, glo_var, min_lon, max_lon, max_lat, min_lat)
