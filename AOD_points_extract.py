import numpy as np
import pandas as pd
from pyhdf.SD import SD
import os
from datetime import datetime


def data_extract(file):
    modis_dataset = SD(modis_file)
    longitude = modis_dataset.select('Longitude')
    latitude = modis_dataset.select('Latitude')
    aod = modis_dataset.select('Image_Optical_Depth_Land_And_Ocean')
    lon_data = longitude.get()
    lat_data = latitude.get()
    aod_data = aod.get()
    aod_attr = aod.attributes()
    _FillValue = aod_attr['_FillValue']
    scale_factor = round(aod_attr['scale_factor'], 3)
    add_offset = aod_attr['add_offset']
    return lon_data, lat_data, aod_data, _FillValue, scale_factor, add_offset


def aod_point_extract(lon_data, lat_data, aod_data, _FillValue, scale_factor, add_offset, point_pass):
    position = pd.read_csv(point_pass)
    for lon_pt, lat_pt in zip(position.loc[:, 'longitude'], position.loc[:, 'latitude']):
        # print(lon_pt, lat_pt)
        x = lon_data - lon_pt
        y = lat_data - lat_pt
        distance = np.sqrt(np.power(x, 2) + np.power(y, 2))
        min_dis = np.min(distance)
        # print(min_dis)
        pos = np.where(distance == min_dis)
        aod_copy = aod_data.copy().astype(float)
        # print(aod_copy.dtype)
        aod_copy[aod_copy == _FillValue] = aod_copy[aod_copy == _FillValue] = 0
        aod_copy[aod_copy != _FillValue] = aod_copy[aod_copy != _FillValue] * scale_factor
        # print(aod_copy)
        extract_aod = aod_copy[pos]
        if extract_aod > 0:
            data_write = open(data_pass + 'extract_aod.txt', 'a')
            print(date, lon_pt, lat_pt, extract_aod, file=data_write)
            print(date, lon_pt, lat_pt, extract_aod)
            data_write.close()


def julian_to_date(julian):
    dt = datetime.strptime(julian, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)


if __name__ == '__main__':
    data_pass = '/mnt/d/Experiments/AOD_Retrieval/DATA/MOD04_3K/'
    point_pass = '/mnt/d/Experiments/AOD_Retrieval/Code/Python/AOD_Extract/position.csv'
    file_list = os.listdir(data_pass)
    for i_file in file_list:
        if i_file.endswith('.hdf') and i_file.startswith('MOD04_3K'):
            modis_file = data_pass + i_file
            julian = i_file[10:17]
            date = julian_to_date(julian)
            lon_data, lat_data, aod_data, _FillValue, scale_factor, add_offset = data_extract(modis_file)
            # print(lon_data, lat_data, aod_data, _FillValue, scale_factor, add_offset)

            aod_point_extract(lon_data, lat_data, aod_data, _FillValue, scale_factor, add_offset, point_pass)
