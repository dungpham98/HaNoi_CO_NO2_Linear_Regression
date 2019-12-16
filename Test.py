import pandas
import datetime
import gdal
import numpy as np

#open tif file using gdal
dataset = gdal.Open(r'lc.tif', gdal.GA_ReadOnly)
#open excel file using pandas
locations = pandas.read_excel(r'HanoiEPAStations.xlsx')
#convert read tif data into a matrix
data = dataset.ReadAsArray()

#Lon of center of first cell/Cell length/_/Lat of center of first cell/_/Cell Width (in Degrees)
geotransform = dataset.GetGeoTransform()
print(geotransform[0], geotransform[1], geotransform[3], geotransform[5])

#cut the excel table and keep only the following columns
locations = locations[['Station ID', 'Lat', 'Lon']]


def extract_by_buffer(locs, buf):
    categories = []
    # get only the selected cell
    if buf is not 0:
        num_of_cells_in_lat = int(buf/geotransform[5])
        num_of_cells_in_lon = int(buf/geotransform[1])

    for i in range(locs.shape[0]):
        count = [0, 0, 0, 0, 0, 0, 0, 0]
        lat_index = int((locs['Lat'][i] - geotransform[3])/geotransform[5])
        lon_index = int((locs['Lon'][i] - geotransform[0])/geotransform[1])
        #get the density value of queried cells and put them in an array
        if buf is not 0:
            for j in range(num_of_cells_in_lat, -num_of_cells_in_lat):
                for k in range(-num_of_cells_in_lon, num_of_cells_in_lon):
                    if np.sqrt(np.power(j*geotransform[5], 2) + np.power(k*geotransform[1], 2)) <= buf:
                        print(data[lat_index-j-1][lon_index-k-1])
                        count[data[lat_index-j-1][lon_index-k-1]] += 1
        #get the value of one cell
        else:
            continue
        categories.append(count)
    return categories


print(extract_by_buffer(locations, 100))
# add the road density as a column in the table-
# locations['Land Cover'] = extract_by_buffer(locations, 0)
# export table as csv
# locations.to_csv(r'D:\Air Pollution Mapping\Group\Data\10EPA_201904\Population Density.csv', index=False)

