import geopy.distance
from shapely.geometry import LineString
import pandas as pd
import numpy as np

#For sintela fiberroute and calibration files
def fiber_channel_locator(das_data, fiber_file = 'fiberroute.csv', cal_file='calibration.csv', chan_spac = 6.3, num_chans = 1750):
    fiber_location = pd.read_csv(fiber_file, header=1)
    fiber_calibration = pd.read_csv(cal_file, header=1)
    fiber_distance = []
    opt_dis_merge = []
    chan_num = []

    for index_fib, row_fib in fiber_location.iterrows():
        if index_fib == 0 :
            fiber_distance.append(0)
        elif index_fib > 0:
            coords_1 = (row_fib['Lat'], row_fib['Long'])
            coords_2 = (fiber_location.iloc[index_fib-1]['Lat'], fiber_location.iloc[index_fib-1]['Long'])
            distance = geopy.distance.geodesic(coords_1, coords_2).m
            fiber_distance.append(distance   + fiber_distance[-1])

        l = []
        for index_cal, row_cal in fiber_calibration.iterrows():
            if row_fib['Lat'] == row_cal['Lat'] and row_fib['Long'] == row_cal['Long']:
                l.append(row_cal['Opt Dist'])
            else:
                pass
        if l:
            opt_dis_merge.append(l[0])
        else:
            opt_dis_merge.append(np.nan)

    fiber_location['Fiber Dist'] = fiber_distance
    fiber_location['Opt Dist'] = opt_dis_merge
    dis_interp = fiber_location['Opt Dist'].interpolate(method='linear', fill_value='extrapolate')
    fiber_location['Opt Dist Interp'] = dis_interp
    
    for index_merge, row_merge in fiber_location.iterrows():
        if row_merge['Opt Dist Interp'] != np.nan:
            
            chan_num.append(row_merge['Opt Dist Interp'] / chan_spac)
            
    fiber_location['Chan Num Interp'] = chan_num
    
    coords_of_chans_x = []
    coords_of_chans_y = []

    channel_number_counter = 0
    for index, values in fiber_location.iterrows():

        if index < len(fiber_location) - 1:
            
            xy_floats = [(fiber_location.iloc[index]['Long'], fiber_location.iloc[index]['Lat']),
                         (fiber_location.iloc[index+1]['Long'], fiber_location.iloc[index+1]['Lat'])]
            line = LineString(xy_floats)
            
            num_points = int(round((fiber_location.iloc[index+1]['Opt Dist Interp'] - values['Opt Dist Interp']) / attrs['SpatialSamplingInterval']))
            channel_number_counter += num_points
            #print(channel_number_counter)
            
            channel_difference = das_data.shape[1] - channel_number_counter
            
            if index == len(fiber_location) - 2:

                num_points = int(round((fiber_location.iloc[index+1]['Opt Dist Interp'] - values['Opt Dist Interp']) / attrs['SpatialSamplingInterval'])) + channel_difference
                print(num_points)
                new_points = [line.interpolate(i/float(num_points - 1), normalized=True) for i in range(num_points)]
                xs = [point.x for point in new_points]
                ys = [point.y for point in new_points]
                coords_of_chans_x.append(xs)
                coords_of_chans_y.append(ys)
            
            else:

                num_points = int(round((fiber_location.iloc[index+1]['Opt Dist Interp'] - values['Opt Dist Interp']) / attrs['SpatialSamplingInterval']))
                new_points = [line.interpolate(i/float(num_points - 1), normalized=True) for i in range(num_points)]
                xs = [point.x for point in new_points]
                ys = [point.y for point in new_points]
                coords_of_chans_x.append(xs)
                coords_of_chans_y.append(ys)
            


            
    

    flat_x =  [item for sublist in coords_of_chans_x for item in sublist] #Longitudes
    flat_y =  [item for sublist in coords_of_chans_y for item in sublist] #Latitudes
    
    return fiber_location, fiber_calibration, flat_x, flat_y